"""
用户相关 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..models.models import User
from ..schemas.schemas import UserCreate, UserResponse, UserUpdate, DataResponse

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **openid**: 用户唯一标识（微信/小程序等）
    - **nickname**: 昵称（可选）
    - **mood_baseline**: 基础情绪分 1-10（可选，默认 5）
    """
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.openid == user_data.openid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户已存在")
    
    # 创建新用户
    new_user = User(
        openid=user_data.openid,
        nickname=user_data.nickname,
        avatar_url=user_data.avatar_url,
        mood_baseline=user_data.mood_baseline
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user(
    openid: str,
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    - **openid**: 用户唯一标识
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已禁用")
    
    return user


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_user(
    user_data: UserUpdate,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    - **nickname**: 新昵称
    - **avatar_url**: 新头像
    - **mood_baseline**: 新基础情绪分
    - **preferences**: 用户偏好
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/{user_id}/stats", response_model=dict, summary="获取用户统计")
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户统计数据
    
    包括：
    - 任务总数/完成数/跳过数
    - 完成率
    - 打卡次数
    - 平均情绪分
    - 连续打卡天数
    """
    from sqlalchemy import func
    from ..models.models import UserTask, Checkin
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 任务统计
    total_tasks = db.query(UserTask).filter(UserTask.user_id == user_id).count()
    completed_tasks = db.query(UserTask).filter(
        UserTask.user_id == user_id,
        UserTask.status == "completed"
    ).count()
    skipped_tasks = db.query(UserTask).filter(
        UserTask.user_id == user_id,
        UserTask.status == "skipped"
    ).count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # 打卡统计
    total_checkins = db.query(Checkin).filter(Checkin.user_id == user_id).count()
    
    avg_mood = db.query(
        func.avg(Checkin.mood_before),
        func.avg(Checkin.mood_after)
    ).filter(Checkin.user_id == user_id).first()
    
    # 连续打卡（简化版）
    current_streak = 0  # TODO: 实现真正的连续打卡计算
    longest_streak = 0  # TODO: 实现真正的最长打卡计算
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "skipped_tasks": skipped_tasks,
        "completion_rate": round(completion_rate, 2),
        "total_checkins": total_checkins,
        "avg_mood_before": round(avg_mood[0], 2) if avg_mood[0] else None,
        "avg_mood_after": round(avg_mood[1], 2) if avg_mood[1] else None,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }
