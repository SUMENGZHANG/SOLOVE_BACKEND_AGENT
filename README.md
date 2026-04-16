# SoLove Backend

情绪陪伴打卡 APP 后端服务

## 项目寓意

**SoLove** = Solo + Love = So Love

> 独自爱自己，也是一种爱

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
solove_backend/
├── app/
│   ├── api/          # API 路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据库模型
│   ├── schemas/      # Pydantic 模型
│   ├── services/     # 业务逻辑
│   └── main.py       # 应用入口
├── tests/            # 测试文件
├── requirements.txt  # 依赖
└── README.md         # 说明文档
```

## 核心功能

- 用户系统（注册/登录）
- 任务管理（创建/分发/打卡）
- Agent 聊天（AI 生成任务）
- 定时推送（每日任务）

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **定时任务**: Celery
- **AI**: 大模型 API

## 开发中

第一阶段 MVP 开发中...
