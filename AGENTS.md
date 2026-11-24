# AGENTS.md — agent-enterprise

## 项目概述
基于 veadk-python 框架的企业级 Agent 平台，支持多 Agent 管理、角色文件配置、模型/Skill/知识库/长期记忆配置、飞书机器人接入与对话 Session 管理。

## 技术栈
- **后端**: Python 3.10+, FastAPI, SQLAlchemy 2.0, Alembic (migration), PyJWT, cryptography (凭据加密)
- **前端**: React 18, Vite, TypeScript, Tailwind CSS, Radix UI, React Router
- **数据库**: SQLite (开发), PostgreSQL (生产)
- **包管理**: pip (后端), npm (前端)

## 目录结构
```
backend/
  app/
    api/v1/       # API 路由
    core/         # 配置、安全、中间件
    db/           # 数据库连接与初始化
    models/       # SQLAlchemy 模型
    schemas/      # Pydantic 模型
    services/     # 业务逻辑层
    tests/        # 测试
  requirements.txt
frontend/
  src/
    api/          # API 客户端
    components/   # 通用组件
    pages/        # 页面
    hooks/        # 自定义 Hooks
    types/        # 类型定义
    lib/          # 工具函数
  package.json
  vite.config.ts
  tailwind.config.js
docs/
```

## 构建与测试
- 后端: `cd backend && pip install -r requirements.txt && pytest`
- 前端: `cd frontend && npm install && npm run build`
- 开发: 后端 `uvicorn app.main:app --reload`, 前端 `npm run dev`

## 编码约定
- 后端 API 统一响应格式: `{ "code": 0, "message": "success", "data": ... }`
- 后端错误码: 0=成功, 1001=参数校验失败, 1002=未认证, 1003=无权限, 1004=不存在, 1005=状态冲突, 2xxx=运行时错误
- 凭据加密: AES-256-Fernet 对称加密, 密钥从环境变量读取
- 前端状态: React Context + useReducer, 不引入额外状态管理库
- 前端路由: React Router v6, 文件约定路由
