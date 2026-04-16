"""
Agent 聊天相关 API（预留）
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from ..core.database import get_db
from ..models.models import User, Conversation
from ..schemas.schemas import ChatMessage, ChatResponse, ConversationResponse

router = APIRouter(prefix="/api/chat", tags=["Agent 聊天"])


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
    
    # TODO: 接入 AI 大模型
    # 目前返回一个占位响应
    response_text = f"我收到你的消息了：'{message_data.message}'。我会认真倾听，陪你一起面对。"
    
    # 保存对话记录
    conversation = Conversation(
        user_id=user.id,
        message=message_data.message,
        response=response_text,
        generated_tasks=None
    )
    db.add(conversation)
    db.commit()
    
    return ChatResponse(
        response=response_text,
        suggested_tasks=None
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
