# Agent 聊天功能实现文档

**日期**: 2026-04-18  
**状态**: ✅ 已完成基础实现

---

## 实现概述

完成了 SoLove 情绪陪伴 Agent 的聊天功能，使用阿里云 Qwen 模型作为底座。

### 核心特性

1. **温暖共情的对话风格** - Agent 人设定位为温柔、不评判的陪伴者
2. **对话历史感知** - 自动获取最近 10 条对话记录，保持上下文连贯
3. **情绪识别** - 当检测到用户情绪低落时，自动分析情绪状态
4. **智能任务建议** - 情绪分低于 5 分时，生成 1-3 个自我关怀建议任务
5. **对话持久化** - 所有对话记录保存到数据库

---

## 技术实现

### 1. AI 服务层 (`app/services/ai_service.py`)

```python
class AIService:
    - chat(): 与 AI 对话
    - analyze_mood(): 情绪分析
    - generate_suggested_tasks(): 生成建议任务
```

**特点**:
- 使用 OpenAI 兼容接口（阿里云 DashScope 支持）
- 未配置 API Key 时自动降级为占位响应
- 支持系统提示词定制 Agent 人设

### 2. API 路由 (`app/api/chat.py`)

```python
POST /api/chat/          # 与 Agent 聊天
GET  /api/chat/history   # 获取聊天历史
```

**聊天流程**:
1. 验证用户（通过 openid）
2. 获取最近 10 条对话历史
3. 调用 AI 服务生成回复
4. 检测情绪关键词，必要时生成建议任务
5. 保存对话记录到数据库

### 3. Agent 人设

```python
AGENT_SYSTEM_PROMPT = """
你是一个温暖的情绪陪伴助手，名叫"SoLove"。

你的特点：
- 温柔、共情、不评判
- 善于倾听，给予情感支持
- 偶尔会建议一些简单的自我关怀小任务
- 说话自然，像朋友一样，不用太正式
"""
```

---

## 文件变更清单

### 新增文件
- `app/services/ai_service.py` - AI 服务模块
- `tests/test_chat.py` - 聊天功能测试
- `test_agent.py` - 快速测试脚本
- `docs/AGENT_CHAT_IMPLEMENTATION.md` - 实现文档

### 修改文件
- `app/api/chat.py` - 实现 AI 聊天逻辑
- `app/main.py` - 注册 chat router
- `requirements.txt` - 添加 openai==1.12.0
- `.env.example` - 添加 AI 配置说明
- `README.md` - 更新核心功能和 API 示例

---

## 配置说明

### 环境变量（.env）

```bash
# AI 配置（阿里云 DashScope / Qwen）
AI_API_KEY=your-dashscope-api-key
AI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-plus
```

**获取 API Key**:
1. 访问 https://dashscope.console.aliyun.com/apiKey
2. 注册/登录阿里云账号
3. 创建 API Key
4. 复制到 .env 文件

---

## 使用示例

### 1. 启动服务

```bash
cd /Users/sumengzhang/Desktop/projects/agent_dev/back_end/solove_backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问 API 文档

浏览器打开：http://localhost:8000/docs

### 3. 测试聊天

```bash
# 使用 curl
curl -X POST "http://localhost:8000/api/chat/?openid=test_user" \
  -H "Content-Type: application/json" \
  -d '{"message": "我今天心情不太好"}'

# 使用测试脚本
python test_agent.py
```

### 4. 运行自动化测试

```bash
pytest tests/test_chat.py -v -s
```

---

## API 响应示例

### 请求
```json
POST /api/chat/?openid=user_123
{
  "message": "我最近很难过，感觉一切都糟透了"
}
```

### 响应
```json
{
  "response": "我能感受到你现在不太好受。没关系，我在这里陪着你，想说什么都可以告诉我。🫂",
  "suggested_tasks": [
    {
      "name": "深呼吸练习",
      "description": "找个安静的地方，深呼吸 5 次，感受气息进出身体",
      "category": "冥想",
      "estimated_time": 3
    },
    {
      "name": "喝一杯温水",
      "description": "慢慢喝一杯温水，感受温度流过身体",
      "category": "自我关怀",
      "estimated_time": 2
    }
  ]
}
```

---

## 下一步计划

### 短期（本周）
- [ ] 配置真实的 AI_API_KEY 进行测试
- [ ] 优化 Agent 人设和回复风格
- [ ] 添加更多情绪关键词识别
- [ ] 完善建议任务模板库

### 中期（下周）
- [ ] 前端对接（小程序/Web）
- [ ] 用户认证系统完善
- [ ] 打卡功能开发
- [ ] 定时推送任务

### 长期
- [ ] 用户情绪趋势分析
- [ ] 个性化任务推荐
- [ ] 多模态交互（语音、图片）
- [ ] 社区功能

---

## 注意事项

1. **API 成本** - Qwen-plus 按 token 计费，注意监控用量
2. **响应延迟** - AI 调用通常需要 1-3 秒，前端需要 loading 状态
3. **对话长度** - 目前限制最近 10 条历史，避免 token 超限
4. **错误处理** - AI 服务不可用时自动降级为占位响应
5. **隐私保护** - 对话数据存储在本地数据库，注意加密和备份

---

## 参考资料

- [阿里云 DashScope 文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI 兼容模式](https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangGraph 学习笔记](./langgraph_know/)
