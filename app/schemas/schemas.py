"""
Pydantic Schemas - API 请求/响应模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 用户相关 ============

class UserBase(BaseModel):
    """用户基础模型"""
    nickname: Optional[str] = Field(None, max_length=64)
    avatar_url: Optional[str] = None
    mood_baseline: Optional[float] = Field(5.0, ge=1, le=10)


class UserCreate(UserBase):
    """用户创建"""
    openid: str = Field(..., max_length=64)


class UserUpdate(BaseModel):
    """用户更新"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    mood_baseline: Optional[float] = Field(None, ge=1, le=10)
    preferences: Optional[dict] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    openid: str
    is_active: bool
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 任务相关 ============

class TaskTemplateBase(BaseModel):
    """任务模板基础"""
    name: str = Field(..., max_length=128)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = "easy"
    estimated_time: Optional[int] = 10


class TaskTemplateCreate(TaskTemplateBase):
    """任务模板创建"""
    pass


class TaskTemplateResponse(TaskTemplateBase):
    """任务模板响应"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserTaskBase(BaseModel):
    """用户任务基础"""
    name: str
    description: Optional[str] = None


class UserTaskCreate(UserTaskBase):
    """用户任务创建"""
    template_id: Optional[int] = None
    date: Optional[datetime] = None


class UserTaskUpdate(BaseModel):
    """用户任务更新"""
    status: Optional[str] = None
    feedback: Optional[str] = None


class UserTaskResponse(UserTaskBase):
    """用户任务响应"""
    id: int
    user_id: int
    template_id: Optional[int]
    date: datetime
    status: str
    completed_at: Optional[datetime]
    feedback: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 打卡相关 ============

class CheckinBase(BaseModel):
    """打卡基础"""
    notes: Optional[str] = None
    mood_before: Optional[float] = Field(None, ge=1, le=10)
    mood_after: Optional[float] = Field(None, ge=1, le=10)


class CheckinCreate(CheckinBase):
    """打卡创建"""
    task_id: int


class CheckinResponse(CheckinBase):
    """打卡响应"""
    id: int
    user_id: int
    task_id: int
    checkin_time: datetime
    
    class Config:
        from_attributes = True


# ============ 对话相关 ============

class ChatMessage(BaseModel):
    """聊天消息"""
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    suggested_tasks: Optional[List[dict]] = None


class ConversationResponse(BaseModel):
    """对话记录响应"""
    id: int
    user_id: int
    message: str
    response: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 统计相关 ============

class UserStats(BaseModel):
    """用户统计"""
    total_tasks: int
    completed_tasks: int
    skipped_tasks: int
    completion_rate: float
    total_checkins: int
    avg_mood_before: Optional[float]
    avg_mood_after: Optional[float]
    current_streak: int
    longest_streak: int


# ============ 通用响应 ============

class ResponseBase(BaseModel):
    """基础响应"""
    success: bool = True
    message: str = "ok"


class DataResponse(ResponseBase):
    """带数据的响应"""
    data: dict = {}
