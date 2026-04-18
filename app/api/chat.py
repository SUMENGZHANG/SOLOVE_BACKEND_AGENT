"""
Agent 聊天相关 API

情绪陪伴 Agent - 使用 Qwen 模型作为底座
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from ..core.database import get_db
from ..models.models import User, Conversation
from ..schemas.schemas import ChatMessage, ChatResponse, ConversationResponse
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api/chat", tags=["Agent 聊天"])

# Agent 人设 - 温暖的情绪陪伴者
AGENT_SYSTEM_PROMPT = """你是一个温暖的情绪陪伴助手，名叫"SoLove"。

你的特点：
- 温柔、共情、不评判
- 善于倾听，给予情感支持
- 偶尔会建议一些简单的自我关怀小任务
- 说话自然，像朋友一样，不用太正式

你的职责：
1. 倾听用户的心声，理解他们的情绪
2. 给予温暖的回应和支持
3. 当用户情绪低落时，可以建议 1-2 个简单的自我关怀任务（不要每次都说）
4. 记住对话上下文，保持连贯性

注意事项：
- 不要说教，不要给复杂的建议
- 如果用户提到严重的心理问题，温和建议寻求专业帮助
- 保持简短温暖的回复（100-300 字）
- 可以用一些 emoji 增加温暖感（🫂✨💙🌟），但不要过度

现在，请开始陪伴用户吧。"""


@router.post("/", response_model=ChatResponse, summary="与 Agent 聊天")
async def chat_with_agent(
    message_data: ChatMessage,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    与 AI Agent 聊天
    
    Agent 会根据对话内容：
    1. 理解用户当前情绪和需求
    2. 给予温暖的回应
    3. 可选：生成建议的任务
    
    - **message**: 用户消息
    """
    # 验证用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取最近的对话历史（最近 10 条）
    recent_conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.created_at.desc()).limit(10).all()
    
    # 构建对话历史（按时间正序）
    messages = []
    for conv in reversed(recent_conversations):
        messages.append({"role": "user", "content": conv.message})
        messages.append({"role": "assistant", "content": conv.response})
    
    # 添加当前消息
    messages.append({"role": "user", "content": message_data.message})
    
    # 调用 AI 服务
    response_text = ai_service.chat(
        messages=messages,
        system_prompt=AGENT_SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=500
    )
    
    # 如果用户情绪明显低落，生成建议任务
    suggested_tasks = None
    low_mood_keywords = ["难过", "伤心", "委屈", "累", "烦", "焦虑", "抑郁", "痛苦", "崩溃", "绝望"]
    if any(word in message_data.message for word in low_mood_keywords):
        # 分析情绪
        mood_analysis = ai_service.analyze_mood(message_data.message)
        mood_score = mood_analysis.get("mood_score", 5.0)
        
        # 如果情绪分低于 5，生成建议任务
        if mood_score < 5:
            conversation_context = "\n".join([m["content"] for m in messages[-4:]])
            suggested_tasks = ai_service.generate_suggested_tasks(
                user_mood=mood_score,
                conversation_context=conversation_context
            )
    
    # 保存对话记录
    conversation = Conversation(
        user_id=user.id,
        message=message_data.message,
        response=response_text,
        generated_tasks=str(suggested_tasks) if suggested_tasks else None
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ChatResponse(
        response=response_text,
        suggested_tasks=suggested_tasks
    )


@router.get("/history", response_model=List[ConversationResponse], summary="获取聊天历史")
async def get_chat_history(
    openid: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取与 Agent 的聊天历史
    
    - **limit**: 返回数量限制（默认 50）
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.created_at.desc()).limit(limit).all()
    
    return conversations
