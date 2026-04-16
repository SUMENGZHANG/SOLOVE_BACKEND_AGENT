"""
打卡相关 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from ..core.database import get_db
from ..models.models import User, Checkin, UserTask
from ..schemas.schemas import CheckinCreate, CheckinResponse

router = APIRouter(prefix="/api/checkins", tags=["打卡"])


@router.post("/", response_model=CheckinResponse, summary="打卡")
async def create_checkin(
    checkin_data: CheckinCreate,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    用户打卡
    
    - **task_id**: 任务 ID
    - **notes**: 打卡备注（可选）
    - **mood_before**: 打卡前情绪分 1-10（可选）
    - **mood_after**: 打卡后情绪分 1-10（可选）
    """
    # 验证用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证任务
    task = db.query(UserTask).filter(
        UserTask.id == checkin_data.task_id,
        UserTask.user_id == user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 创建打卡记录
    new_checkin = Checkin(
        user_id=user.id,
        task_id=checkin_data.task_id,
        notes=checkin_data.notes,
        mood_before=checkin_data.mood_before,
        mood_after=checkin_data.mood_after
    )
    db.add(new_checkin)
    
    # 更新任务状态为已完成
    task.status = "completed"
    task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(new_checkin)
    
    return new_checkin


@router.get("/my", response_model=List[CheckinResponse], summary="获取我的打卡记录")
async def get_my_checkins(
    openid: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取用户的打卡记录
    
    - **limit**: 返回数量限制（默认 50）
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    checkins = db.query(Checkin).filter(
        Checkin.user_id == user.id
    ).order_by(Checkin.checkin_time.desc()).limit(limit).all()
    
    return checkins


@router.get("/stats", response_model=dict, summary="获取打卡统计")
async def get_checkin_stats(
    openid: str,
    db: Session = Depends(get_db)
):
    """
    获取打卡统计数据
    """
    from sqlalchemy import func
    
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 总打卡次数
    total = db.query(Checkin).filter(Checkin.user_id == user.id).count()
    
    # 平均情绪分
    avg_mood = db.query(
        func.avg(Checkin.mood_before),
        func.avg(Checkin.mood_after)
    ).filter(Checkin.user_id == user.id).first()
    
    # 最近 7 天打卡次数
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)
    week_count = db.query(Checkin).filter(
        Checkin.user_id == user.id,
        Checkin.checkin_time >= week_ago
    ).count()
    
    return {
        "total_checkins": total,
        "avg_mood_before": round(avg_mood[0], 2) if avg_mood[0] else None,
        "avg_mood_after": round(avg_mood[1], 2) if avg_mood[1] else None,
        "mood_improvement": round(avg_mood[1] - avg_mood[0], 2) if (avg_mood[0] and avg_mood[1]) else None,
        "checkins_last_7_days": week_count
    }
