"""
数据库模型定义
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), unique=True, index=True, comment="用户唯一标识")
    nickname = Column(String(64), comment="昵称")
    avatar_url = Column(String(255), comment="头像 URL")
    
    # 情绪相关
    mood_baseline = Column(Float, default=5.0, comment="基础情绪分值 (1-10)")
    preferences = Column(Text, comment="用户偏好 (JSON)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_premium = Column(Boolean, default=False, comment="是否付费会员")
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联
    tasks = relationship("UserTask", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class TaskTemplate(Base):
    """任务模板表"""
    __tablename__ = "task_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, comment="任务名称")
    description = Column(Text, comment="任务描述")
    category = Column(String(64), comment="分类：运动/阅读/冥想/社交/自我关怀")
    difficulty = Column(String(16), default="easy", comment="难度：easy/medium/hard")
    estimated_time = Column(Integer, default=10, comment="预计耗时 (分钟)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserTask(Base):
    """用户任务表（每日生成）"""
    __tablename__ = "user_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("task_templates.id"), nullable=True)
    
    # 任务内容
    name = Column(String(128), nullable=False, comment="任务名称")
    description = Column(Text, comment="任务描述")
    date = Column(DateTime(timezone=True), nullable=False, comment="任务日期")
    
    # 状态
    status = Column(String(16), default="pending", comment="状态：pending/completed/skipped")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    feedback = Column(Text, comment="完成后的反馈/感受")
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    user = relationship("User", back_populates="tasks")
    checkins = relationship("Checkin", back_populates="task", cascade="all, delete-orphan")


class Checkin(Base):
    """打卡记录表"""
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("user_tasks.id"), nullable=False)
    
    # 打卡内容
    notes = Column(Text, comment="打卡备注")
    mood_before = Column(Float, comment="打卡前情绪分 (1-10)")
    mood_after = Column(Float, comment="打卡后情绪分 (1-10)")
    
    # 时间
    checkin_time = Column(DateTime(timezone=True), server_default=func.now(), comment="打卡时间")
    
    # 关联
    user = relationship("User", back_populates="checkins")
    task = relationship("UserTask", back_populates="checkins")


class Conversation(Base):
    """对话记录表（Agent 接入后用）"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 对话内容
    message = Column(Text, nullable=False, comment="用户消息")
    response = Column(Text, nullable=False, comment="AI 回复")
    generated_tasks = Column(Text, comment="生成的任务 (JSON)")
    
    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    user = relationship("User", back_populates="conversations")
