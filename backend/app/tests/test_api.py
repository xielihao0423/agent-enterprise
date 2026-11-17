"""Minimal integration tests for the Agent Enterprise Platform API."""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add user site-packages for sqlalchemy etc.
sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.10/site-packages"))

from app.main import app
from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.core.security import hash_password

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Create tables and default admin before tests."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(username="admin", hashed_password=hash_password("admin123"), display_name="Admin")
        db.add(admin)
        db.commit()
    db.close()
    yield
    # Cleanup: drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def auth_headers():
    """Login and return auth headers."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    def test_login_success(self):
        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]

    def test_login_wrong_password(self):
        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
        assert response.json()["code"] == 1002

    def test_unauthorized_access(self):
        response = client.get("/api/v1/agents")
        assert response.status_code == 401


class TestAgentCRUD:
    def test_create_agent(self, auth_headers):
        response = client.post("/api/v1/agents", json={"name": "测试Agent", "description": "测试描述"}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "测试Agent"
        assert data["data"]["status"] == "draft"

    def test_list_agents(self, auth_headers):
        response = client.get("/api/v1/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]["items"]) >= 1

    def test_get_agent(self, auth_headers):
        # Create first
        create_resp = client.post("/api/v1/agents", json={"name": "获取测试"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        # Get
        response = client.get(f"/api/v1/agents/{agent_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "获取测试"

    def test_update_agent(self, auth_headers):
        create_resp = client.post("/api/v1/agents", json={"name": "更新前"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        response = client.put(f"/api/v1/agents/{agent_id}", json={"name": "更新后"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "更新后"

    def test_delete_agent(self, auth_headers):
        create_resp = client.post("/api/v1/agents", json={"name": "删除测试"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        response = client.delete(f"/api/v1/agents/{agent_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_duplicate_agent(self, auth_headers):
        create_resp = client.post("/api/v1/agents", json={"name": "复制原"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        response = client.post(f"/api/v1/agents/{agent_id}/duplicate", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "复制原_copy"
        assert response.json()["data"]["status"] == "draft"


class TestRoleFiles:
    def test_get_role_files(self, auth_headers):
        create_resp = client.post("/api/v1/agents", json={"name": "角色文件测试"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        response = client.get(f"/api/v1/agents/{agent_id}/role-files", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert "agent_md" in data
        assert "user_md" in data
        assert "identity_md" in data
        assert "soul_md" in data

    def test_update_role_file(self, auth_headers):
        create_resp = client.post("/api/v1/agents", json={"name": "角色更新测试"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        response = client.put(f"/api/v1/agents/{agent_id}/role-files/agent_md", json={"content": "# Agent Instructions"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["version"] == 2  # First save creates version 1 (empty), this is version 2

    def test_role_file_versions(self, auth_headers):
        create_resp = client.post("/api/v1/agents", json={"name": "版本测试"}, headers=auth_headers)
        agent_id = create_resp.json()["data"]["id"]
        # Create multiple versions
        client.put(f"/api/v1/agents/{agent_id}/role-files/identity_md", json={"content": "v1 content"}, headers=auth_headers)
        client.put(f"/api/v1/agents/{agent_id}/role-files/identity_md", json={"content": "v2 content"}, headers=auth_headers)
        response = client.get(f"/api/v1/agents/{agent_id}/role-files/identity_md/versions", headers=auth_headers)
        assert response.status_code == 200
        versions = response.json()["data"]
        assert len(versions) >= 2


class TestModelProvider:
    def test_create_provider(self, auth_headers):
        response = client.post("/api/v1/model-providers", json={
            "provider_type": "ark",
            "name": "ARK测试",
            "api_key": "test-api-key-12345678",
            "base_url": "https://ark.cn-beijing.volces.com",
            "available_models": ["doubao-pro-32k", "doubao-lite-32k"]
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_list_providers(self, auth_headers):
        response = client.get("/api/v1/model-providers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 1
        # Verify key is masked
        assert "****" in data[0]["api_key_masked"]

    def test_test_provider(self, auth_headers):
        create_resp = client.post("/api/v1/model-providers", json={
            "provider_type": "openai",
            "name": "OpenAI测试",
            "api_key": "sk-test-key-1234567890",
            "available_models": ["gpt-4", "gpt-3.5-turbo"]
        }, headers=auth_headers)
        provider_id = create_resp.json()["data"]["id"]
        response = client.post(f"/api/v1/model-providers/{provider_id}/test", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "available"


class TestSession:
    def test_create_and_message(self, auth_headers):
        # Create agent
        agent_resp = client.post("/api/v1/agents", json={"name": "会话测试Agent"}, headers=auth_headers)
        agent_id = agent_resp.json()["data"]["id"]
        # Create provider and bind model
        prov_resp = client.post("/api/v1/model-providers", json={
            "provider_type": "ark", "name": "测试供应商",
            "api_key": "test-key-12345678", "available_models": ["doubao-pro-32k"]
        }, headers=auth_headers)
        provider_id = prov_resp.json()["data"]["id"]
        client.put(f"/api/v1/model-providers/agents/{agent_id}/model", json={
            "provider_id": provider_id, "model_name": "doubao-pro-32k"
        }, headers=auth_headers)
        # Activate agent
        client.patch(f"/api/v1/agents/{agent_id}/status", json={"status": "active"}, headers=auth_headers)
        # Create session
        sess_resp = client.post(f"/api/v1/agents/{agent_id}/sessions", json={"source": "web"}, headers=auth_headers)
        assert sess_resp.status_code == 200
        session_id = sess_resp.json()["data"]["id"]
        # Send message
        msg_resp = client.post(f"/api/v1/sessions/{session_id}/messages", json={"content": "你好"}, headers=auth_headers)
        assert msg_resp.status_code == 200
        assert msg_resp.json()["data"]["role"] == "assistant"
        assert "你好" in msg_resp.json()["data"]["content"]


class TestSkill:
    def test_install_and_bind(self, auth_headers):
        # Install skill
        skill_resp = client.post("/api/v1/skills", json={"name": "web_search", "description": "网页搜索", "version": "1.0.0"}, headers=auth_headers)
        skill_id = skill_resp.json()["data"]["id"]
        # Create agent
        agent_resp = client.post("/api/v1/agents", json={"name": "Skill测试"}, headers=auth_headers)
        agent_id = agent_resp.json()["data"]["id"]
        # Bind
        bind_resp = client.post(f"/api/v1/agents/{agent_id}/skills", json={"skill_id": skill_id}, headers=auth_headers)
        assert bind_resp.status_code == 200
        # Toggle
        toggle_resp = client.patch(f"/api/v1/agents/{agent_id}/skills/{skill_id}", json={"enabled": False}, headers=auth_headers)
        assert toggle_resp.status_code == 200
        assert toggle_resp.json()["data"]["enabled"] == False
