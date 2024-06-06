from logging import getLogger
from uuid import UUID
from typing import List, Union

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.task import _create_new_task
from api.actions.task import _delete_task
from api.actions.task import _get_task_by_id
from api.actions.task import _update_task
from api.actions.task import _get_tasks_by_created_for

from api.actions.auth import get_current_user_from_token

from api.schemas import TaskCreate, ShowTask, UpdateTask, UpdatedTaskResponse, DeleteTaskResponse
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

@task_router.delete("/tasks/{task_id}", response_model=DeleteTaskResponse)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> DeleteTaskResponse:
    deleted_task_id = await _delete_task(task_id, db)
    return DeleteTaskResponse(deleted_task_id=deleted_task_id)

@task_router.put("/tasks/{task_id}", response_model=UpdatedTaskResponse)
async def update_task(
    task_id: UUID,
    updated_task: UpdateTask,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> UpdatedTaskResponse:
    updated_task_id = await _update_task(updated_task.dict(), task_id, db)
    return UpdatedTaskResponse(updated_task_id=updated_task_id)

@task_router.get("/tasks/{task_id}", response_model=Union[ShowTask, None])
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    task = await _get_task_by_id(task_id, db)
    if task:
        return ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_for=task.created_for,
            created_by=task.created_by,
            is_active=task.is_active,
        )
    return None

@task_router.get("/tasks/created_for/{created_for}", response_model=List[ShowTask])
async def get_tasks_by_created_for(
    created_for: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    tasks = await _get_tasks_by_created_for(created_for, db)
    return [
        ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_for=task.created_for,
            created_by=task.created_by,
            is_active=task.is_active,
        ) for task in tasks
    ]
