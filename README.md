# SOLOVE_BACKEND_AGENT

SoLove Backend

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

### ✅ 已完成
- **用户系统** - 注册/登录/用户信息管理
- **Agent 聊天** - 情绪陪伴 AI（Qwen 模型）
  - 温暖共情的对话风格
  - 情绪识别与分析
  - 智能生成建议任务（当用户情绪低落时）
  - 对话历史持久化

### 🚧 开发中
- **任务管理** - 创建/分发/打卡
- **定时推送** - 每日任务提醒

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL（`mysql+pymysql://...`）
- **缓存**: Redis
- **定时任务**: Celery
- **AI**: Qwen（阿里云 DashScope）

## API 使用示例

### 与 Agent 聊天

```bash
# 发送消息
curl -X POST "http://localhost:8000/api/chat/?openid=your_user_id" \
  -H "Content-Type: application/json" \
  -d '{"message": "我今天心情不太好"}'

# 响应示例
{
  "response": "我能感受到你现在不太好受。没关系，我在这里陪着你...",
  "suggested_tasks": [
    {
      "name": "深呼吸 3 次",
      "description": "找个舒服的姿势，深呼吸 3 次...",
      "category": "冥想",
      "estimated_time": 2
    }
  ]
}
```

### 获取聊天历史

```bash
curl "http://localhost:8000/api/chat/history?openid=your_user_id&limit=50"
```

## AI 配置

使用阿里云 DashScope（Qwen 模型）：

1. 获取 API Key: https://dashscope.console.aliyun.com/apiKey
2. 在 `.env` 中配置：
   ```
   AI_API_KEY=your-dashscope-api-key
   AI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   AI_MODEL=qwen-plus
   ```

## 测试

```bash
# 运行聊天功能测试
pytest tests/test_chat.py -v -s
```
