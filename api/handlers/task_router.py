from logging import getLogger
from uuid import UUID
from typing import Union

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.task import _create_new_task
from api.actions.task import _delete_task
from api.actions.task import _get_task_by_id
from api.actions.task import _update_task

from api.actions.auth import get_current_user_from_token

from api.schemas import TaskCreate, ShowTask
from db.models import User
from db.session import get_db

logger = getLogger(__name__)

task_router = APIRouter()

@task_router.post("/tasks/", response_model=ShowTask)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    return await _create_new_task(task, db, current_user)

@task_router.delete("/tasks/{task_id}", response_model=Union[UUID, None])
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    return await _delete_task(task_id, db)

@task_router.put("/tasks/{task_id}", response_model=Union[UUID, None])
async def update_task(
    task_id: UUID,
    updated_task_params: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    return await _update_task(updated_task_params, task_id, db)

@task_router.get("/tasks/{task_id}", response_model=Union[ShowTask, None])
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    task = await _get_task_by_id(task_id, db)
    if task:
        return ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_by=task.created_by,
            is_active=task.is_active,
        )
    return None
