# 部署文档 — 企业级 Agent 平台

## 环境要求

- Python 3.10+
- Node.js 18+
- npm 10+
- SQLite（开发环境内置）或 PostgreSQL（生产环境）

## 后端部署

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
SECRET_KEY=your-secret-key-at-least-32-characters-long
ENCRYPTION_KEY=your-fernet-key-for-credential-encryption
DATABASE_URL=sqlite:///./agent_enterprise.db
DEBUG=true
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

生产环境使用 PostgreSQL：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/agent_enterprise
```

### 3. 启动服务

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

首次启动会自动创建数据库表和默认管理员账号（admin/admin123）。

### 2.1 Agent 运行时（veadk-python）

对话执行由 [veadk-python](https://github.com/volcengine/veadk-python) 的 `Agent` / `Runner` 驱动
（见 `backend/app/services/agent_runtime.py`）。`requirements.txt` 已包含 `veadk-python`。

运行前提：
- 需在平台「模型配置」中创建模型供应商并绑定到已启用的 Agent（至少一个模型绑定）。
- 模型供应商的 API Key 以 Fernet 加密存储，运行时解密后注入 veadk Agent，不会落盘或打印。
- Agent 的 `Agent.md` / `USER.md` / `IDENTITY.md` / `SOUL.md` 四类角色文件会按当前版本拼接为
  instruction 注入运行时上下文。

feishu/ARK 示例（火山方舟）：

```env
# 可选：veadk 默认模型密钥；平台内模型供应商凭据优先
MODEL_AGENT_API_KEY=your-ark-api-key
```

说明：当 `veadk-python` 未安装、Agent 未绑定模型或凭据无效时，`POST /api/v1/sessions/{id}/messages`
会返回明确的错误响应（`code != 0`），**不会**返回硬编码的模拟回复；前端对话界面会以红色错误气泡展示该错误。

### 4. 验证

```bash
curl http://localhost:8000/health
# {"code":0,"message":"success","data":{"status":"healthy"}}
```

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
npm run dev
# 启动在 http://localhost:5173，API 代理到 http://localhost:8000
```

### 3. 生产构建

```bash
npm run build
# 产物在 frontend/dist/
```

### 4. 预览构建产物

```bash
npm run preview
```

## Docker 部署（可选）

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY backend/ /app/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 默认账号

- 用户名：admin
- 密码：admin123
- **首次登录后请修改密码**

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
