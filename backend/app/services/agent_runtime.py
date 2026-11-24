"""Runtime adapter that executes an Agent through veadk-python.

This module bridges the platform's persisted Agent configuration (role files,
model binding, provider credentials) to the veadk ``Agent`` / ``Runner``
primitives. It deliberately does NOT fabricate assistant replies: when the
runtime or its configuration is unavailable it raises ``AgentRuntimeError`` so
the API layer can surface an explicit, truthful error instead of a mock answer.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.models.agent import Agent, RoleFile
from app.models.model_provider import AgentModelBinding, ModelProvider
from app.models.session import Session as SessionModel, Message
from app.core.security import decrypt_credential

# Mapping of role-file type -> heading used when composing the instruction.
ROLE_FILE_HEADINGS = {
    "agent_md": "AGENT",
    "user_md": "USER",
    "identity_md": "IDENTITY",
    "soul_md": "SOUL",
}

# Provider type -> veadk/LiteLLM model provider prefix.
PROVIDER_TYPE_MAP = {
    "ark": "openai",   # ARK is OpenAI-compatible; base_url points at ARK endpoint
    "openai": "openai",
}

DEFAULT_ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


class AgentRuntimeError(Exception):
    """Raised when the agent cannot be executed (runtime missing or misconfigured)."""


@dataclass
class RuntimeResult:
    content: str
    token_usage: int = 0
    tool_calls: Optional[list] = None


def _build_instruction(db: Session, agent: Agent) -> str:
    """Compose the instruction/context from the agent's current role files."""
    parts: list[str] = []
    for file_type, heading in ROLE_FILE_HEADINGS.items():
        rf = (
            db.query(RoleFile)
            .filter(
                RoleFile.agent_id == agent.id,
                RoleFile.file_type == file_type,
                RoleFile.is_current == True,  # noqa: E712
            )
            .first()
        )
        if rf and rf.content and rf.content.strip():
            parts.append(f"# {heading}\n{rf.content.strip()}")

    if not parts:
        # Fall back to a minimal instruction from the agent description.
        return agent.description or f"你是一个名为 {agent.name} 的助手。"

    parts.append(
        "# Response Rule\n"
        "Respond directly to the user. Do not describe your internal setup, "
        "do not mention method names or frameworks, and do not emit placeholder text."
    )
    return "\n\n".join(parts)


def _resolve_model_config(db: Session, agent: Agent) -> dict:
    """Resolve veadk model parameters from the agent's model binding + provider."""
    binding = (
        db.query(AgentModelBinding)
        .filter(AgentModelBinding.agent_id == agent.id)
        .first()
    )
    if not binding:
        raise AgentRuntimeError("Agent 未绑定模型，无法执行对话")

    provider = (
        db.query(ModelProvider).filter(ModelProvider.id == binding.provider_id).first()
    )
    if not provider:
        raise AgentRuntimeError("Agent 绑定的模型供应商不存在")

    try:
        api_key = decrypt_credential(provider.api_key_encrypted)
    except Exception as exc:  # noqa: BLE001
        raise AgentRuntimeError("模型凭据解密失败") from exc
    if not api_key:
        raise AgentRuntimeError("模型供应商缺少有效 API Key")

    provider_prefix = PROVIDER_TYPE_MAP.get(provider.provider_type, provider.provider_type)
    base_url = provider.base_url or (
        DEFAULT_ARK_BASE_URL if provider.provider_type == "ark" else None
    )

    # Strip any provider prefix that may have been stored on the model name so
    # we do not double-prefix (veadk builds "model_provider/model_name").
    model_name = binding.model_name
    if model_name.startswith(f"{provider_prefix}/"):
        model_name = model_name[len(provider_prefix) + 1:]

    return {
        "model_provider": provider_prefix,
        "model_name": model_name,
        "model_api_key": api_key,
        "model_api_base": base_url,
        "temperature": binding.temperature,
        "max_tokens": binding.max_tokens,
        "top_p": binding.top_p,
    }


def _build_history(db: Session, session_id: int) -> list[dict]:
    """Load prior messages to preserve conversation context across turns."""
    msgs = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [{"role": m.role, "content": m.content or ""} for m in msgs if m.role in ("user", "assistant")]


def _create_veadk_agent(agent: Agent, instruction: str, model_cfg: dict):
    """Instantiate a veadk Agent. Imported lazily so the API can start without veadk."""
    try:
        from veadk import Agent as VeAgent
    except ImportError as exc:  # noqa: BLE001
        raise AgentRuntimeError(
            "veadk-python 运行时未安装，无法执行 Agent。请安装 veadk-python 依赖。"
        ) from exc

    return VeAgent(
        name=agent.name or "agent",
        description=agent.description or "",
        instruction=instruction,
        model_name=model_cfg["model_name"],
        model_provider=model_cfg["model_provider"],
        model_api_key=model_cfg["model_api_key"],
        model_api_base=model_cfg["model_api_base"],
        model_extra_config={
            "extra_body": {
                "temperature": model_cfg["temperature"],
                "max_tokens": model_cfg["max_tokens"],
                "top_p": model_cfg["top_p"],
            }
        },
    )


async def _run_async(ve_agent, messages, user_id: str, session_id: str) -> str:
    from veadk import Runner
    runner = Runner(agent=ve_agent, app_name="agent_enterprise")
    return await runner.run(messages=messages, user_id=user_id, session_id=session_id)


def run_agent(
    db: Session,
    agent: Agent,
    session: SessionModel,
    user_message: str,
    history: Optional[list[dict]] = None,
) -> RuntimeResult:
    """Execute the agent against the latest user message and return its reply.

    Raises ``AgentRuntimeError`` when the runtime is unavailable or misconfigured.
    """
    if agent.status != "active":
        raise AgentRuntimeError("Agent 未启用，无法执行对话")

    instruction = _build_instruction(db, agent)
    model_cfg = _resolve_model_config(db, agent)
    ve_agent = _create_veadk_agent(agent, instruction, model_cfg)

    # Build the conversation input. veadk Runner consumes a text prompt per turn
    # and keeps its own short-term memory keyed by session_id; we pass the full
    # history as a single structured prompt so context survives restarts.
    user_id = session.user_id or "web_user"
    runner_session_id = f"agent-{agent.id}-session-{session.id}"

    if history:
        transcript = "\n".join(
            f"{'用户' if h['role'] == 'user' else '助手'}: {h['content']}"
            for h in history
            if h.get("content")
        )
        prompt = (
            f"以下是此前的对话记录：\n{transcript}\n\n"
            f"用户最新消息：{user_message}"
        )
    else:
        prompt = user_message

    try:
        # FastAPI endpoints are sync; veadk's Runner.run is async. Run it on a
        # dedicated event loop to avoid clashing with an already-running loop.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                content = executor.submit(
                    lambda: asyncio.run(
                        _run_async(ve_agent, prompt, user_id, runner_session_id)
                    )
                ).result()
        else:
            content = asyncio.run(
                _run_async(ve_agent, prompt, user_id, runner_session_id)
            )
    except AgentRuntimeError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AgentRuntimeError(f"Agent 执行失败: {exc}") from exc

    if not content or not str(content).strip():
        raise AgentRuntimeError("Agent 未返回有效回复")

    content = str(content).strip()
    # Rough token estimate; real usage is available from veadk tracers when enabled.
    token_usage = max(1, len(content) // 4)
    return RuntimeResult(content=content, token_usage=token_usage, tool_calls=None)
