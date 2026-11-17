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
