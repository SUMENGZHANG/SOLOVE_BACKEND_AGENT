"""
任务相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

from ..core.database import get_db
from ..models.models import User, UserTask, TaskTemplate
from ..schemas.schemas import (
    UserTaskCreate, UserTaskUpdate, UserTaskResponse,
    TaskTemplateCreate, TaskTemplateResponse
)

router = APIRouter(prefix="/api/tasks", tags=["任务"])


@router.get("/today", response_model=List[UserTaskResponse], summary="获取今日任务")
async def get_today_tasks(
    openid: str,
    db: Session = Depends(get_db)
):
    """
    获取用户今日任务
    
    返回今天需要完成的所有任务
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    today = date.today()
    tasks = db.query(UserTask).filter(
        UserTask.user_id == user.id,
        UserTask.date >= datetime.combine(today, datetime.min.time()),
        UserTask.date < datetime.combine(today, datetime.max.time())
    ).all()
    
    return tasks


@router.get("/history", response_model=List[UserTaskResponse], summary="获取历史任务")
async def get_task_history(
    openid: str,
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    db: Session = Depends(get_db)
):
    """
    获取用户历史任务
    
    - **days**: 查询最近 N 天的任务（默认 7 天，最多 30 天）
    """
    from datetime import timedelta
    
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    start_date = date.today() - timedelta(days=days)
    tasks = db.query(UserTask).filter(
        UserTask.user_id == user.id,
        UserTask.date >= datetime.combine(start_date, datetime.min.time())
    ).order_by(UserTask.date.desc()).all()
    
    return tasks


@router.post("/create", response_model=UserTaskResponse, summary="创建任务")
async def create_task(
    task_data: UserTaskCreate,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    创建用户任务
    
    - **name**: 任务名称
    - **description**: 任务描述
    - **template_id**: 任务模板 ID（可选）
    - **date**: 任务日期（可选，默认今天）
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 创建任务
    new_task = UserTask(
        user_id=user.id,
        template_id=task_data.template_id,
        name=task_data.name,
        description=task_data.description,
        date=task_data.date or datetime.now()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


@router.put("/{task_id}", response_model=UserTaskResponse, summary="更新任务状态")
async def update_task(
    task_id: int,
    task_data: UserTaskUpdate,
    db: Session = Depends(get_db)
):
    """
    更新任务状态
    
    - **status**: 新状态（pending/completed/skipped）
    - **feedback**: 完成后的反馈
    """
    task = db.query(UserTask).filter(UserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # 如果状态改为 completed，设置完成时间
    if task_data.status == "completed":
        task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}", summary="删除任务")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """删除任务"""
    task = db.query(UserTask).filter(UserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    
    return {"success": True, "message": "任务已删除"}


# ============ 任务模板 ============

@router.get("/templates", response_model=List[TaskTemplateResponse], summary="获取任务模板列表")
async def get_task_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取任务模板列表
    
    - **category**: 按分类筛选（可选）
    """
    query = db.query(TaskTemplate).filter(TaskTemplate.is_active == True)
    
    if category:
        query = query.filter(TaskTemplate.category == category)
    
    return query.all()


@router.post("/templates", response_model=TaskTemplateResponse, summary="创建任务模板")
async def create_task_template(
    template_data: TaskTemplateCreate,
    db: Session = Depends(get_db)
):
    """创建任务模板"""
    new_template = TaskTemplate(**template_data.model_dump())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template
