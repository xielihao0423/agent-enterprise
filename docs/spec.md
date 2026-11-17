# Review Summary

- 本次需求: 基于 veadk-python 框架开发企业级 Agent 平台，支持多 Agent 管理、角色文件配置、模型/Skill/知识库/长期记忆配置、飞书机器人接入与对话 Session 管理，单租户私有化部署。
- 需求类型: UX / Backend / Open API / Data model / Metrics / NFR / Permission-security
- 变更面: Functional Requirements (REQ-001~REQ-009), UX Design, Backend/Data, API Design, Metrics, NFR/DFX, Traceability, Open Questions; 不涉及: 无（全新项目，全部模块需从零设计）; 待确认: TD-1~TD-8 技术选型项（不阻塞 Spec 定稿，移交技术设计节点）
- 变更面判断依据: 需求澄清文档（docs/需求澄清.md）、目标仓库 xielihao0423/agent-enterprise 为空白初始仓库、veadk-python 框架能力调研、产品知识库技术栈上下文
- 差异判断: 产品形态差异: 不涉及（单租户私有化，无多形态分支）; 站点差异: 不涉及（单站点部署）; 环境差异: 待确认（私有化部署环境的具体 OS/容器/网络约束未指定）; 版本差异: 不涉及（全新项目无历史版本兼容问题）; 依据: 需求澄清文档确认单租户私有化部署，目标仓库为空白初始提交
- 本次变更关键信息:
  - 新增 9 个功能需求模块（REQ-001~REQ-009），覆盖多 Agent 管理、角色文件版本化、模型配置、Skill 管理、知识库配置、长期记忆配置、飞书机器人接入、对话 Session 管理、前后端架构
  - 重要范围决策：首期单租户私有化，不做多租户/SaaS/计费/配额；飞书机器人首期仅文本+附件，不做卡片消息/交互按钮
  - 重要风险：veadk-python 框架 API 封装深度（TD-6）影响平台与框架耦合度；8 项技术选型待技术设计节点确认
- Review 重点:
  - Scope: 确认 9 个 REQ 模块是否完整覆盖需求澄清的范围
  - API compatibility: REST API 契约设计是否足以支撑前后端分离开发
  - Data model: Agent/角色文件/模型/Skill/知识库/记忆/Session/飞书机器人 的数据模型与关系是否完整
  - Security: 凭据加密、鉴权、审计方案是否明确
  - Rollout: 私有化部署架构与 veadk-python 依赖是否可行

## Scope Note

- Implemented sections: Context, Goals and Non-Goals, Glossary, Functional Requirements (REQ-001~REQ-009), UX Design, Backend/Data, API Design, Metrics, NFR/DFX, Open Questions, Traceability
- Not involved: 无（全新项目从零搭建，所有模块均在范围内）
- Needs confirmation: TD-1 前端技术栈选型 / TD-2 后端框架选型 / TD-3 数据持久化方案 / TD-4 凭据加密方案 / TD-5 飞书机器人接入方式 / TD-6 veadk-python API 封装策略 / TD-7 角色文件版本化存储方案 / TD-8 用户认证方案
- Reason: 目标仓库为空白初始提交，需求澄清已确认全部业务契约，8 项技术选型不阻塞 Spec 定稿但需技术设计节点逐一确认。

---

# Spec: 企业级 Agent 平台（基于 veadk-python）

## 1. Context

本 Spec 基于需求澄清文档 `docs/需求澄清.md`（产物 ID: `xielihao0423/agent-enterprise@b5a8e2a`）生成。

**澄清文档增量说明（Spec 阶段）：**
- 澄清文档已确认全部 4 项业务契约（部署形态、用户规模、模型供应商、飞书机器人范围），Spec 不重复展开。
- 8 项技术待设计（TD-1~TD-8）在 Spec 中以 Open Questions 形式登记，并给出基于证据的推荐方向，最终方案由技术设计节点确认。
- Spec 阶段新增：REST API 契约设计、数据模型与持久化方案建议、前端 UX 模块划分、Metrics 口径定义、NFR 约束细化。
- 关联参考框架：veadk-python（https://github.com/volcengine/veadk-python），提供 Agent/Runner/Session/Memory/KnowledgeBase/Skills/FeishuChannelExtension/Tracing 等核心能力。

## 2. Goals and Non-Goals

沿用需求澄清文档的目标与非目标。Spec 阶段补充以下增量：

**Goals 增量：**
| 目标 | 衡量方式 | 目标值 / 判断标准 |
|------|----------|-------------------|
| 平台 API 可支撑前后端分离开发 | API 文档完整度 | 所有 REQ 对应的 REST API 端点有明确的 request/response schema |
| 关键链路有自动化测试 | 测试覆盖率 | Agent CRUD、模型配置、飞书消息接入、Session 管理核心链路有集成测试 |
| 可观测性覆盖 | 指标完备度 | 请求日志、Agent 执行轨迹、Token 用量、错误监控四类指标可查询 |

**Non-Goals 增量（Spec 阶段收窄）：**
- 不做实时流式响应的前端 SSE/WebSocket 推送优化（首期使用标准 HTTP 请求/响应）。
- 不做 Agent 间的编排/协作/多 Agent 对话（首期每个 Agent 独立运行）。
- 不做模型路由/负载均衡/故障转移（首期每个 Agent 绑定单一模型）。

## 3. Glossary

| 术语 | 含义 |
|------|------|
| veadk-python | 火山引擎开源的 Python Agent 开发框架，提供 Agent/Runner/Session/Memory/KnowledgeBase/Skills/FeashuChannelExtension 等模块 |
| Agent.md / USER.md / IDENTITY.md / SOUL.md | 四类角色文件，分别定义 Agent 的通用指令、用户上下文、身份信息和性格灵魂，运行时注入上下文 |
| ARK | 火山引擎方舟（Volcengine ARK），提供豆包系列大模型 API |
| Runner | veadk-python 中负责 Agent 执行循环的组件，管理 LLM 调用、Tool 执行和响应生成 |
| Session | veadk-python 中的会话管理组件，维护对话上下文和历史消息 |
| Memory | veadk-python 中的长期记忆组件，支持按作用域存储和检索记忆 |
| KnowledgeBase | veadk-python 中的知识库组件，支持文档上传、解析、索引和检索 |
| Skills | veadk-python 中的技能组件，封装可被 Agent 调用的工具能力 |
| FeishuChannelExtension | veadk-python 中的飞书渠道扩展，支持飞书机器人消息收发 |
| 推理档位 | 模型推理参数配置，如 temperature、max_tokens、top_p 等 |

## 4. Functional Requirements

### REQ-001: 多 Agent 管理

- **User Story**: As a 平台管理员, I want 创建、编辑、启停、删除和复制 Agent, so that 管理多个 AI Agent 的全生命周期。
- **Priority**: P0
- **Description**: 管理员可在管理台创建 Agent 并配置基本属性（名称、描述、头像），编辑 Agent 配置，启用/停用 Agent，删除 Agent（软删除），以及复制已有 Agent 配置创建新 Agent。Agent 列表支持搜索和状态筛选。

Acceptance Requirements (EARS):
- REQ-001.1: The system shall allow creating an Agent with name (required), description (optional), and avatar (optional).
- REQ-001.2: When an Agent is created, the system shall assign a unique Agent ID and set initial status to "draft".
- REQ-001.3: The system shall support Agent status transitions: draft → active → inactive → active (可循环), draft/active/inactive → deleted.
- REQ-001.4: When an Agent is duplicated, the system shall copy all configuration (角色文件、模型、Skill 绑定、知识库绑定、记忆参数) to a new Agent with status "draft", and the new Agent's name shall be suffixed with "_copy".
- REQ-001.5: If an Agent is "active" and associated with active Sessions, the system shall prevent deletion and return an error message indicating active Sessions exist.
- REQ-001.6: The system shall support searching Agents by name and filtering by status (all/draft/active/inactive/deleted).

Gherkin:
```gherkin
Scenario: 创建并启用 Agent
  Given 管理员已登录管理台
  When 管理员填写 Agent 名称"客服助手"并提交创建
  Then 系统创建 Agent，状态为 "draft"
  When 管理员点击"启用"
  Then Agent 状态变为 "active"，可接收对话请求

Scenario: 复制 Agent
  Given 存在一个 "active" 状态的 Agent "客服助手"，已配置角色文件、模型和 Skill
  When 管理员点击"复制"
  Then 系统创建新 Agent "客服助手_copy"，状态为 "draft"，继承全部配置
```

### REQ-002: Agent 角色文件配置

- **User Story**: As a 平台管理员, I want 配置和版本化管理 Agent.md、USER.md、IDENTITY.md、SOUL.md 四类角色文件, so that Agent 运行时有正确的身份和指令上下文。
- **Priority**: P0
- **Description**: 每个 Agent 可独立配置四类角色文件内容（Markdown 文本）。角色文件支持版本化维护，每次保存生成新版本，历史版本可查看和回溯。运行时按当前生效版本注入 Agent 上下文。

Acceptance Requirements (EARS):
- REQ-002.1: The system shall store four role file types per Agent: Agent.md, USER.md, IDENTITY.md, SOUL.md.
- REQ-002.2: When a role file is saved, the system shall create a new version with version number, timestamp, and operator.
- REQ-002.3: The system shall allow viewing historical versions of each role file and restoring a specific historical version as the current version.
- REQ-002.4: When Agent Runner executes, the system shall inject the current effective version of all four role files into the Agent context.
- REQ-002.5: If a role file is empty, the system shall skip injection of that file and not raise an error.

Gherkin:
```gherkin
Scenario: 角色文件版本回溯
  Given Agent "客服助手" 的 IDENTITY.md 已有 3 个版本
  When 管理员查看版本历史并选择恢复到版本 2
  Then 版本 2 的内容成为当前生效版本，系统生成新版本号（基于版本 2 内容）
```

### REQ-003: 模型配置

- **User Story**: As a 平台管理员, I want 配置火山引擎 ARK 和 OpenAI 两类模型供应商的接入凭据、默认模型与推理档位, so that Agent 可以调用合适的 LLM。
- **Priority**: P0
- **Description**: 管理员可在平台级配置模型供应商（ARK / OpenAI），包括 API Key（加密存储）、Base URL、可用模型列表。每个 Agent 绑定一个默认模型和推理档位（temperature、max_tokens、top_p）。

Acceptance Requirements (EARS):
- REQ-003.1: The system shall support configuring two model providers: Volcengine ARK and OpenAI.
- REQ-003.2: The system shall encrypt model API Keys at rest using symmetric encryption; API responses and frontend display shall mask the key (showing only last 4 characters).
- REQ-003.3: When a model provider is configured, the system shall validate the API Key by sending a test request to the provider's API.
- REQ-003.4: The system shall allow each Agent to bind one default model and configure inference parameters (temperature, max_tokens, top_p) with sensible defaults.
- REQ-003.5: If a model API call fails, the system shall return a structured error response with error type (auth/quota/timeout/unknown) and retry guidance.

Gherkin:
```gherkin
Scenario: 配置模型供应商凭据
  Given 管理员已登录管理台
  When 管理员选择 "Volcengine ARK" 并输入 API Key
  Then 系统加密存储 API Key，前端仅显示 "****<最后4位>"
  When 系统发送测试请求验证凭据
  Then 验证成功后该模型供应商状态为 "可用"

Scenario: Agent 绑定模型
  Given Agent "客服助手" 处于编辑状态
  When 管理员选择模型 "doubao-pro-32k" 并设置 temperature=0.7
  Then Agent 默认模型更新为 "doubao-pro-32k"，推理档位生效
```

### REQ-004: Skill 配置

- **User Story**: As a 平台管理员, I want 安装 Skill 到平台级 Skill 库并按 Agent 绑定/解绑和启停, so that Agent 可按需使用工具能力。
- **Priority**: P1
- **Description**: Skill 安装到平台级 Skill 库后，Agent 可按需绑定/解绑。绑定后可按 Agent 级别启停。Skill 版本更新后可选择是否升级。

Acceptance Requirements (EARS):
- REQ-004.1: The system shall maintain a platform-level Skill library where Skills can be installed with name, description, version, and source.
- REQ-004.2: The system shall allow binding/unbinding Skills to/from an Agent from the Skill library.
- REQ-004.3: When a Skill is bound to an Agent, the system shall allow enabling/disabling it at the Agent level independently.
- REQ-004.4: When a Skill in the library has a version update, the system shall notify (via UI badge) Agents bound to the Skill and allow the administrator to choose whether to upgrade.
- REQ-004.5: If a Skill execution throws an exception during Agent Runner execution, the system shall catch the error, log it, and continue the conversation with an error message to the user.

Gherkin:
```gherkin
Scenario: Skill 绑定与启停
  Given 平台 Skill 库中有 "web_search" Skill v1.0
  And Agent "客服助手" 未绑定该 Skill
  When 管理员将 "web_search" 绑定到 "客服助手"
  Then 绑定关系建立，默认状态为 "enabled"
  When 管理员将该绑定切换为 "disabled"
  Then Agent 运行时不加载该 Skill
```

### REQ-005: 知识库配置

- **User Story**: As a 平台管理员, I want 创建知识库、上传文档并按 Agent 绑定与配置检索参数, so that Agent 可基于知识库内容回答问题。
- **Priority**: P1
- **Description**: 知识库为平台级资源，可被多个 Agent 绑定。每个绑定关系可独立配置检索参数（Top-K、相似度阈值）。文档上传后自动解析和索引。

Acceptance Requirements (EARS):
- REQ-005.1: The system shall allow creating knowledge bases with name and description at the platform level.
- REQ-005.2: When a document is uploaded to a knowledge base, the system shall automatically parse, chunk, and index the document; supported formats include PDF, TXT, Markdown, DOCX.
- REQ-005.3: The system shall allow binding a knowledge base to multiple Agents, with each binding having independent retrieval parameters (Top-K default: 3, similarity threshold default: 0.7).
- REQ-005.4: When Agent Runner retrieves from a knowledge base, the system shall use the binding's retrieval parameters to filter and return relevant chunks.
- REQ-005.5: If document parsing or indexing fails, the system shall mark the document status as "failed" with an error reason and allow re-upload.

Gherkin:
```gherkin
Scenario: 知识库绑定与检索配置
  Given 知识库 "产品文档库" 已创建并索引了 10 篇文档
  And Agent "客服助手" 未绑定该知识库
  When 管理员将 "产品文档库" 绑定到 "客服助手"，设置 Top-K=5、阈值=0.8
  Then 绑定关系建立，Agent 运行时检索参数为 Top-K=5、阈值=0.8
```

### REQ-006: 长期记忆配置

- **User Story**: As a 平台管理员, I want 配置 Agent 的长期记忆开关、作用域、写入策略和清理规则, so that Agent 可跨会话记住和遗忘信息。
- **Priority**: P1
- **Description**: 记忆作用域分为 Agent 级、用户级、会话级三级。写入策略支持自动写入和手动写入。记忆可按作用域检索和清理。

Acceptance Requirements (EARS):
- REQ-006.1: The system shall support three memory scopes: Agent-level (shared across all sessions of the Agent), user-level (scoped to a specific user across sessions), and session-level (scoped to a single session).
- REQ-006.2: The system shall allow enabling/disabling memory per Agent, with separate toggles for each scope.
- REQ-006.3: When memory write strategy is "auto", the system shall automatically extract and store relevant information from each conversation turn into the configured scopes.
- REQ-006.4: When memory write strategy is "manual", the system shall not auto-write; memory entries can be added via API or management UI.
- REQ-006.5: The system shall allow viewing and deleting memory entries by scope (Agent/user/session).
- REQ-006.6: If memory retrieval fails, the system shall log the error and continue the conversation without memory context (degraded mode).

Gherkin:
```gherkin
Scenario: 自动记忆写入
  Given Agent "客服助手" 已启用 Agent 级和用户级记忆，写入策略为 "auto"
  When 用户 "张三" 在 Session 中提到 "我的部门是技术部"
  Then 系统自动提取并存储用户级记忆条目 "张三的部门是技术部"
  When "张三" 在新的 Session 中开始对话
  Then Agent 上下文包含用户级记忆，Agent 可引用该信息
```

### REQ-007: 飞书机器人接入

- **User Story**: As a 平台管理员, I want 创建飞书机器人并绑定到 Agent, so that 终端用户可通过飞书单聊或群聊与 Agent 对话。
- **Priority**: P0
- **Description**: 管理员可创建飞书机器人（配置 App ID、App Secret），绑定到一个 Agent。支持 Webhook 或长连接方式接入。飞书单聊映射为该用户的独立 Session，群聊映射为群维度的共享 Session。消息收发支持文本和文件附件。

Acceptance Requirements (EARS):
- REQ-007.1: The system shall allow creating a Feishu bot with App ID (required) and App Secret (required, encrypted at rest).
- REQ-007.2: The system shall bind one Feishu bot to one Agent (1:1 relationship).
- REQ-007.3: When a Feishu bot receives a single-chat message, the system shall map it to a user-scoped Session for the bound Agent.
- REQ-007.4: When a Feishu bot receives a group-chat message, the system shall map it to a group-scoped Session (shared by all group members) for the bound Agent.
- REQ-007.5: The system shall support sending and receiving text messages and file attachments via Feishu bot.
- REQ-007.6: If the Feishu connection (Webhook/long-polling) disconnects, the system shall automatically retry reconnection and log a warning.
- REQ-007.7: If a Feishu bot is not bound to any Agent, the system shall reject incoming messages with an error log.

Gherkin:
```gherkin
Scenario: 飞书单聊消息接入
  Given 飞书机器人 "客服Bot" 已绑定到 Agent "客服助手"
  When 用户 "张三" 通过飞书单聊发送 "你好"
  Then 系统将消息映射到 Agent "客服助手" 的 "张三" 用户级 Session
  And Agent Runner 执行后通过飞书回复文本消息

Scenario: 飞书群聊消息接入
  Given 飞书机器人 "客服Bot" 已绑定到 Agent "客服助手" 并加入群 "技术支持群"
  When 群成员 "张三" 在群内 @客服Bot 发送 "如何重置密码"
  Then 系统将消息映射到 Agent "客服助手" 的 "技术支持群" 群级 Session
  And Agent Runner 执行后通过飞书在群内回复文本消息
```

### REQ-008: 对话与 Session 管理

- **User Story**: As a 终端用户/管理员, I want 进行多会话对话并管理 Session 上下文, so that 可以在隔离的上下文中与 Agent 交互并查看历史记录。
- **Priority**: P0
- **Description**: 一个 Agent 可有多个 Session。Session 间上下文隔离。支持查看历史消息、中断当前执行和续跑。会话状态可查询。

Acceptance Requirements (EARS):
- REQ-008.1: The system shall support multiple Sessions per Agent, each with isolated conversation context.
- REQ-008.2: The system shall allow listing Sessions for an Agent with status (idle/running/interrupted/closed), last message timestamp, and message count.
- REQ-008.3: When a Session is in "running" state, the system shall allow the user to interrupt the execution, transitioning the Session to "interrupted" state.
- REQ-008.4: When a Session is "interrupted", the system shall allow resuming (续跑) from the existing context, transitioning back to "running" and then "idle" upon completion.
- REQ-008.5: The system shall store and allow viewing complete message history for each Session, including user messages, Agent responses, tool call traces, and timestamps.
- REQ-008.6: If a Session is "closed", the system shall prevent new messages and mark it as read-only.

Gherkin:
```gherkin
Scenario: Session 中断与续跑
  Given Agent "客服助手" 的 Session A 状态为 "running"（Agent 正在执行）
  When 用户点击 "中断"
  Then Session A 状态变为 "interrupted"，已生成的内容保留
  When 用户点击 "续跑"
  Then Session A 状态变为 "running"，基于已有上下文继续执行
  And 执行完成后状态变为 "idle"
```

### REQ-009: 前后端架构

- **User Story**: As a 平台管理员和终端用户, I want 通过 Web 管理台和对话界面使用平台, so that 可以完成 Agent 配置和对话交互。
- **Priority**: P0
- **Description**: 后端提供 REST API 与鉴权、数据持久化、运行时编排（基于 veadk-python）。前端提供管理台（Agent 配置、模型/Skill/知识库/记忆管理、Session 查看）和对话界面（多会话交互、历史消息、附件发送）。

Acceptance Requirements (EARS):
- REQ-009.1: The system shall provide a REST API backend with authentication for all endpoints.
- REQ-009.2: The system shall persist all configuration data (Agents, role files, model configs, Skill bindings, knowledge bases, memory configs, Feishu bots, Sessions) in a database.
- REQ-009.3: The system shall use veadk-python's Agent/Runner/Session/Memory/KnowledgeBase/Skills/FeishuChannelExtension modules for runtime orchestration, wrapping them in a platform service layer.
- REQ-009.4: The frontend management console shall provide pages for: Agent list & detail, model configuration, Skill library, knowledge base management, memory management, Feishu bot management, Session list & detail, and execution trace viewing.
- REQ-009.5: The frontend chat interface shall support: selecting an Agent, creating/listing Sessions, sending text/file messages, viewing message history, interrupting/resuming execution.
- REQ-009.6: The system shall require authentication for all API access; unauthenticated requests shall return 401.

Gherkin:
```gherkin
Scenario: 管理员通过前端完成 Agent 全链路配置
  Given 管理员已登录管理台
  When 管理员创建 Agent → 编辑角色文件 → 绑定模型 → 绑定 Skill → 绑定知识库 → 配置记忆 → 绑定飞书机器人 → 启用 Agent
  Then Agent 状态为 "active"，终端用户可通过飞书或前端对话界面与 Agent 交互

Scenario: 终端用户通过前端对话界面交互
  Given Agent "客服助手" 为 "active" 状态
  When 用户在前端选择该 Agent 并创建新 Session
  Then 系统创建空 Session，用户可发送消息并收到 Agent 回复
```

## 5. UX Design

### 体验目标与设计原则
- 管理台以信息密度和操作效率为主，采用左侧导航 + 右侧内容区布局。
- 对话界面以消息流为核心，支持多 Session 侧边栏切换。
- 配置流程采用分步/分 Tab 组织，避免单页过长。

### 页面 / 模块 / 入口范围

**管理台（Admin Console）：**
| 模块 | 页面 | 核心功能 |
|------|------|----------|
| Agent 管理 | Agent 列表 / Agent 详情 | Agent CRUD、状态切换、复制；详情页含角色文件/模型/Skill/知识库/记忆/机器人 Tab |
| 模型配置 | 模型供应商列表 / 模型详情 | 供应商配置、凭据管理、可用模型列表、测试连接 |
| Skill 库 | Skill 列表 | Skill 安装、版本查看、绑定状态总览 |
| 知识库 | 知识库列表 / 知识库详情 | 知识库 CRUD、文档上传与状态查看、绑定管理 |
| 记忆管理 | 记忆查看 | 按 Agent/用户/会话查看和清理记忆条目 |
| 飞书机器人 | 机器人列表 / 机器人详情 | 机器人 CRUD、Agent 绑定、连接状态查看 |
| Session 管理 | Session 列表 / Session 详情 | Session 列表筛选、消息历史查看、执行轨迹查看 |
| 审计与监控 | 审计日志 / 指标看板 | 操作审计日志、Token 用量、错误监控 |

**对话界面（Chat UI）：**
| 模块 | 核心功能 |
|------|----------|
| Agent 选择 | 下拉/列表选择 active 状态的 Agent |
| Session 侧边栏 | 创建/切换/关闭 Session，显示最近消息摘要 |
| 消息流 | 显示历史消息，支持文本和附件展示 |
| 输入区 | 文本输入、文件上传、发送、中断/续跑按钮 |

### 核心体验路径
1. 管理员登录 → 创建 Agent → 逐 Tab 完成配置 → 启用 Agent
2. 终端用户选择 Agent → 创建 Session → 发送消息 → 收到回复

### 分支路径 / 异常路径
- Empty: Agent 列表为空时显示引导创建按钮；Session 列表为空时显示引导新建对话。
- Loading: Agent 执行中显示 "思考中..." 动画；文档上传/索引中显示进度状态。
- Permission denied: 未登录访问任何页面跳转登录页。
- Submit failure: 模型凭据测试失败显示错误原因；Agent 启用前校验必配项（至少有模型绑定）。
- Retry: 飞书消息发送失败显示重试按钮；Agent 回复超时显示超时提示。

### 文案与可理解性
- Agent 状态用中文标签：草稿/已启用/已停用/已删除。
- 错误消息使用用户可理解的中文描述，不暴露技术细节。
- 角色文件编辑器提供 Markdown 预览。

### 视觉与响应式约束
- 首期仅支持桌面端（最小宽度 1280px），不做移动端适配。
- 待确认：前端技术栈选型（TD-1），推荐 React + Vite + Tailwind CSS（与团队现有技术栈一致）。

## 6. Backend/Data

### 行为与验证规则
- Agent 创建时自动生成唯一 ID，状态初始化为 "draft"。
- Agent 启用前校验：至少绑定一个模型；角色文件至少配置 Agent.md。
- 模型凭据写入时加密存储，读取时解密但不返回给前端。
- 角色文件每次保存生成版本快照，版本号自增。
- 知识库文档上传后异步解析索引，状态流转：uploading → parsing → indexing → ready / failed。
- Session 创建时初始化空上下文；消息追加时更新上下文；中断时保留已有内容。
- 飞书消息接收后，根据 chat_type（P2P/group）映射到对应 Session，无匹配 Session 时自动创建。

### 状态流转

**Agent 状态机：**
| 操作 | 前置状态 | 目标状态 | 校验 |
|------|----------|----------|------|
| 创建 | — | draft | — |
| 启用 | draft / inactive | active | 至少绑定一个模型 |
| 停用 | active | inactive | — |
| 删除 | draft / inactive | deleted | 无 active Session |
| 恢复 | deleted | draft | — |

**Session 状态机：**
| 操作 | 前置状态 | 目标状态 |
|------|----------|----------|
| 创建 | — | idle |
| 发送消息 | idle | running |
| 执行完成 | running | idle |
| 中断 | running | interrupted |
| 续跑 | interrupted | running |
| 关闭 | idle / interrupted | closed |

**文档处理状态机：**
| 操作 | 前置状态 | 目标状态 |
|------|----------|----------|
| 上传 | — | uploading |
| 解析 | uploading | parsing |
| 索引 | parsing | indexing |
| 完成 | indexing | ready |
| 失败 | uploading/parsing/indexing | failed |
| 重试 | failed | uploading |

### 权限检查
- 所有 API 需认证（JWT Token），未认证返回 401。
- 单租户部署，无角色区分（首期所有认证用户有全部管理权限）。
- 待确认：是否需要区分管理员和终端用户角色（TD-8）。

### 存储模型（建议方案，最终方案待技术设计确认）

核心实体与关系：
- **Agent**: id, name, description, avatar, status, created_at, updated_at
- **RoleFile**: id, agent_id, file_type (Agent.md/USER.md/IDENTITY.md/SOUL.md), content, version, created_at, operator
- **ModelProvider**: id, provider_type (ark/openai), api_key_encrypted, base_url, available_models, status
- **AgentModelBinding**: id, agent_id, provider_id, model_name, temperature, max_tokens, top_p
- **Skill**: id, name, description, version, source, installed_at
- **AgentSkillBinding**: id, agent_id, skill_id, enabled, bound_at
- **KnowledgeBase**: id, name, description, created_at
- **Document**: id, kb_id, filename, file_path, status, error_reason, uploaded_at
- **AgentKBBinding**: id, agent_id, kb_id, top_k, similarity_threshold
- **MemoryConfig**: id, agent_id, scope_enabled (agent/user/session), write_strategy (auto/manual)
- **MemoryEntry**: id, agent_id, scope, user_id, session_id, content, created_at
- **FeishuBot**: id, app_id, app_secret_encrypted, agent_id, connection_mode (webhook/long_polling), status
- **Session**: id, agent_id, user_id, source (feishu/web), chat_type (single/group), status, created_at
- **Message**: id, session_id, role (user/assistant/tool), content, attachments, token_usage, created_at
- **AuditLog**: id, operator, action, target_type, target_id, detail, created_at

### 失败处理与幂等性
- Agent 启用操作幂等：已 active 的 Agent 再次启用不报错。
- 文档上传支持重试：相同文件名重新上传覆盖失败记录。
- Session 创建幂等：飞书消息映射时，相同 chat_id + agent_id 已有 Session 则复用。

### 迁移/兼容性
- 全新项目无历史数据迁移。数据库 schema 使用 migration 脚本管理版本。
- 待确认：数据持久化方案（TD-3），推荐 PostgreSQL（veadk-python Memory 已支持）+ Redis（Session 状态缓存）。

## 7. API Design

> 本节定义平台 REST API 契约，供前后端分离开发和飞书机器人后端对接使用。

### 认证
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 登录 | POST | /api/v1/auth/login | 用户名/密码认证，返回 JWT Token |
| 登出 | POST | /api/v1/auth/logout | 使 Token 失效 |
| 当前用户 | GET | /api/v1/auth/me | 获取当前登录用户信息 |

### Agent 管理
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| Agent 列表 | GET | /api/v1/agents | 支持 status/name 筛选和分页 |
| 创建 Agent | POST | /api/v1/agents | 创建新 Agent |
| Agent 详情 | GET | /api/v1/agents/{agent_id} | 获取 Agent 完整配置 |
| 更新 Agent | PUT | /api/v1/agents/{agent_id} | 更新 Agent 基本属性 |
| 删除 Agent | DELETE | /api/v1/agents/{agent_id} | 软删除 Agent |
| 启用/停用 | PATCH | /api/v1/agents/{agent_id}/status | 切换 Agent 状态 |
| 复制 Agent | POST | /api/v1/agents/{agent_id}/duplicate | 复制 Agent 及全部配置 |

### 角色文件
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 获取角色文件 | GET | /api/v1/agents/{agent_id}/role-files | 获取四类角色文件当前内容 |
| 更新角色文件 | PUT | /api/v1/agents/{agent_id}/role-files/{file_type} | 保存角色文件（生成新版本） |
| 版本历史 | GET | /api/v1/agents/{agent_id}/role-files/{file_type}/versions | 获取版本列表 |
| 恢复版本 | POST | /api/v1/agents/{agent_id}/role-files/{file_type}/versions/{version}/restore | 恢复指定版本 |

### 模型配置
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 供应商列表 | GET | /api/v1/model-providers | 获取已配置的模型供应商 |
| 创建供应商 | POST | /api/v1/model-providers | 配置新供应商（凭据加密存储） |
| 更新供应商 | PUT | /api/v1/model-providers/{provider_id} | 更新供应商配置 |
| 测试连接 | POST | /api/v1/model-providers/{provider_id}/test | 测试 API Key 有效性 |
| Agent 模型绑定 | PUT | /api/v1/agents/{agent_id}/model | 绑定模型与推理参数 |

### Skill 配置
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| Skill 库列表 | GET | /api/v1/skills | 获取平台 Skill 列表 |
| 安装 Skill | POST | /api/v1/skills | 安装新 Skill |
| Agent Skill 绑定 | POST | /api/v1/agents/{agent_id}/skills | 绑定 Skill 到 Agent |
| 解绑 Skill | DELETE | /api/v1/agents/{agent_id}/skills/{skill_id} | 解绑 Skill |
| 切换启停 | PATCH | /api/v1/agents/{agent_id}/skills/{skill_id} | 切换 Skill 启用/停用 |

### 知识库
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 知识库列表 | GET | /api/v1/knowledge-bases | 获取知识库列表 |
| 创建知识库 | POST | /api/v1/knowledge-bases | 创建新知识库 |
| 上传文档 | POST | /api/v1/knowledge-bases/{kb_id}/documents | 上传文档（multipart） |
| 文档列表 | GET | /api/v1/knowledge-bases/{kb_id}/documents | 获取文档及处理状态 |
| Agent KB 绑定 | POST | /api/v1/agents/{agent_id}/knowledge-bases | 绑定知识库与检索参数 |
| 解绑 KB | DELETE | /api/v1/agents/{agent_id}/knowledge-bases/{kb_id} | 解绑知识库 |

### 长期记忆
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 记忆配置 | GET/PUT | /api/v1/agents/{agent_id}/memory-config | 获取/更新记忆开关与策略 |
| 记忆条目 | GET | /api/v1/agents/{agent_id}/memories | 按 scope/user_id/session_id 筛选 |
| 删除记忆 | DELETE | /api/v1/agents/{agent_id}/memories/{memory_id} | 删除指定记忆条目 |
| 批量清理 | DELETE | /api/v1/agents/{agent_id}/memories | 按 scope 批量清理 |

### 飞书机器人
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 机器人列表 | GET | /api/v1/feishu-bots | 获取机器人列表 |
| 创建机器人 | POST | /api/v1/feishu-bots | 创建机器人（凭据加密存储） |
| 绑定 Agent | PUT | /api/v1/feishu-bots/{bot_id}/agent | 绑定机器人到 Agent |
| 连接状态 | GET | /api/v1/feishu-bots/{bot_id}/status | 获取连接状态 |

### Session 与对话
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| Session 列表 | GET | /api/v1/agents/{agent_id}/sessions | 获取 Session 列表 |
| 创建 Session | POST | /api/v1/agents/{agent_id}/sessions | 创建新 Session |
| Session 详情 | GET | /api/v1/sessions/{session_id} | 获取 Session 状态和信息 |
| 消息历史 | GET | /api/v1/sessions/{session_id}/messages | 分页获取消息历史 |
| 发送消息 | POST | /api/v1/sessions/{session_id}/messages | 发送消息并触发 Agent 执行 |
| 中断执行 | POST | /api/v1/sessions/{session_id}/interrupt | 中断当前执行 |
| 续跑 | POST | /api/v1/sessions/{session_id}/resume | 续跑已中断的 Session |
| 关闭 Session | PATCH | /api/v1/sessions/{session_id}/status | 关闭 Session |

### 审计与监控
| API | 方法 | 路径 | 说明 |
|-----|------|------|------|
| 审计日志 | GET | /api/v1/audit-logs | 分页获取操作审计日志 |
| Token 用量 | GET | /api/v1/metrics/token-usage | 按 Agent/时间范围查询 Token 用量 |
| 执行轨迹 | GET | /api/v1/sessions/{session_id}/traces | 获取 Agent 执行轨迹 |
| 错误统计 | GET | /api/v1/metrics/errors | 按时间范围查询错误统计 |

### 通用响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```
错误响应：
```json
{
  "code": <非0错误码>,
  "message": "<用户可理解的错误描述>",
  "data": null
}
```

### 错误码约定
| 错误码 | HTTP Status | 含义 |
|--------|-------------|------|
| 0 | 200 | 成功 |
| 1001 | 400 | 参数校验失败 |
| 1002 | 401 | 未认证 |
| 1003 | 403 | 无权限 |
| 1004 | 404 | 资源不存在 |
| 1005 | 409 | 状态冲突（如删除有 active Session 的 Agent） |
| 2001 | 500 | 模型调用失败 |
| 2002 | 500 | Skill 执行异常 |
| 2003 | 500 | 知识库检索超时 |
| 2004 | 503 | 飞书连接异常 |

## 8. Metrics

| 指标 | 触发点 | 属性 | 关联 REQ |
|------|--------|------|----------|
| 请求日志 | 每次 API 调用 | method, path, status_code, latency, user_id, timestamp | REQ-009 |
| Agent 执行轨迹 | Agent Runner 每次执行 | agent_id, session_id, model_name, input_tokens, output_tokens, tool_calls, duration, status | REQ-008, REQ-009 |
| Token 用量 | 每次模型调用 | agent_id, model_provider, model_name, input_tokens, output_tokens, timestamp | REQ-003 |
| 错误监控 | 运行时异常 | error_type, error_message, agent_id, session_id, timestamp | REQ-003~REQ-008 |
| 审计日志 | 关键操作（Agent CRUD、模型配置变更、Skill 绑定/解绑、机器人配置） | operator, action, target_type, target_id, detail, timestamp | REQ-001, REQ-003, REQ-004, REQ-007 |

### Dashboard / 审查频率
- Token 用量看板：按 Agent 维度日/周汇总，管理员可查看趋势。
- 错误统计看板：按错误类型和时间维度汇总，支持查看明细。
- 审计日志：支持按操作类型、操作人、时间范围筛选查看。

## 9. NFR / DFX

| 类别 | 要求 | 验收方法 |
|------|------|----------|
| 安全 | 模型 API Key、飞书 App Secret 等敏感凭据使用对称加密存储，API 响应脱敏 | 验证数据库中凭据字段为密文；API 响应中凭据字段为掩码 |
| 安全 | 所有 API 需认证后访问 | 未带 Token 的请求返回 401 |
| 安全 | 关键操作记录审计日志 | 执行 Agent CRUD 等操作后验证审计日志记录 |
| 可观测性 | 请求日志、Agent 执行轨迹、Token 用量、错误监控可查询 | 通过 Metrics API 验证四类指标可查询 |
| 可扩展性 | 模型、Skill、知识库、飞书机器人适配器采用接口化设计 | 新增模型供应商只需实现 ModelProvider 接口，不修改平台核心代码 |
| 可扩展性 | veadk-python 框架升级时平台层改动最小化 | 平台通过 service 层封装 veadk-python API，不直接在业务逻辑中调用框架 |
| 可用性 | 飞书连接断开后自动重连，重连间隔指数退避 | 模拟断连后验证自动重连和告警日志 |
| 可用性 | 模型调用失败/Skill 异常/知识库检索超时有降级策略 | 模拟各类异常验证降级行为（错误反馈而非系统崩溃） |
| 性能 | 单 Agent 对话响应延迟（不含模型推理时间）<500ms | 对 API 发送消息到 Agent Runner 启动的平台处理时间进行基准测试 |
| 部署 | 单租户私有化部署，提供部署文档 | 按部署文档可在全新环境完成部署 |
| 环境差异 | 待确认：私有化部署环境的具体 OS/容器/网络约束 | 需确认目标部署环境后补充 |

## Open Questions

| ID | 问题 | 影响 | 建议方向 | 建议处理节点 |
|---|---|---|---|---|
| OQ-001 (TD-1) | 前端技术栈选型：React+Vite+Tailwind vs Vue3+Vite+Element Plus | 前端组件生态、开发效率、后续维护成本 | React + Vite + Tailwind CSS（与团队现有技术栈一致，产品知识库中 deliveryai-demo-xielihaotest 使用该栈） | 技术设计节点 |
| OQ-002 (TD-2) | 后端框架选型：FastAPI vs Django REST Framework | API 开发效率、ORM 选型、项目结构 | FastAPI（异步、轻量、与 veadk-python 同为 Python 生态） | 技术设计节点 |
| OQ-003 (TD-3) | 数据持久化方案：PostgreSQL vs PostgreSQL+Redis | 部署复杂度、性能、Session 恢复能力 | PostgreSQL + Redis（PostgreSQL 存元数据，Redis 做 Session 状态缓存；veadk-python Memory 已支持 PostgreSQL） | 技术设计节点 |
| OQ-004 (TD-4) | 凭据加密方案：AES-256+KMS vs 对称加密+环境变量密钥 | 安全等级、部署复杂度 | 对称加密 + 环境变量密钥（轻量私有化方案，满足小团队安全需求） | 技术设计节点 |
| OQ-005 (TD-5) | 飞书机器人接入方式：长连接 vs Webhook vs 两者均支持 | 部署网络要求、消息实时性 | 首期支持长连接（实时性好，无需公网暴露），后续按需扩展 Webhook | 技术设计节点 |
| OQ-006 (TD-6) | veadk-python Agent/Runner/Session/Memory API 封装策略 | 平台与框架耦合度、可维护性 | 技术设计节点详细调研 veadk-python API 后确定平台层封装策略 | 技术设计节点 |
| OQ-007 (TD-7) | 角色文件版本化存储方案：数据库版本快照 vs Git 仓库存储 | 版本回溯效率、存储成本 | 数据库存储版本快照（简单、小团队够用） | 技术设计节点 |
| OQ-008 (TD-8) | 用户认证方案：内置用户名/密码+JWT vs 企业 SSO vs 两者均支持 | 部署复杂度、企业集成成本 | 首期内置用户名/密码 + JWT（快速交付），后续按需对接 SSO | 技术设计节点 |

## Traceability

| REQ ID | UX 章节 | API 章节 | Backend/Data | Metrics | NFR | QA 重点 |
|--------|---------|----------|-------------|---------|------|---------|
| REQ-001 | Agent 管理页 | Agent 管理 API | Agent 实体、状态机 | 审计日志 | 安全/可扩展 | Agent CRUD、状态流转、复制 |
| REQ-002 | Agent 详情-角色文件 Tab | 角色文件 API | RoleFile 实体、版本管理 | 审计日志 | — | 角色文件编辑、版本回溯 |
| REQ-003 | 模型配置页 | 模型配置 API | ModelProvider、AgentModelBinding | Token 用量 | 安全/可扩展 | 凭据加密、模型绑定、测试连接 |
| REQ-004 | Skill 库页、Agent 详情-Skill Tab | Skill API | Skill、AgentSkillBinding | 审计日志 | 可扩展 | Skill 安装、绑定/解绑、启停 |
| REQ-005 | 知识库管理页 | 知识库 API | KnowledgeBase、Document、AgentKBBinding | — | 可扩展 | 文档上传/解析/索引、绑定检索参数 |
| REQ-006 | 记忆管理页 | 记忆 API | MemoryConfig、MemoryEntry | — | 可用性 | 记忆开关、作用域、写入策略、清理 |
| REQ-007 | 飞书机器人管理页 | 飞书机器人 API | FeishuBot、Session 映射 | 请求日志/错误监控 | 安全/可用性 | 机器人创建/绑定、单聊/群聊映射、消息收发 |
| REQ-008 | 对话界面、Session 管理页 | Session API | Session、Message、状态机 | 执行轨迹 | 可用性 | 多会话、上下文隔离、中断/续跑 |
| REQ-009 | 全部前端页面 | 认证 API + 全部业务 API | 全部实体、veadk-python 封装 | 全部指标 | 安全/可观测/可扩展/部署 | 鉴权、前后端联调、部署验证 |
