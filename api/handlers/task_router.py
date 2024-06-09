from logging import getLogger
from uuid import UUID
from typing import List, Union

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.actions.task import _create_new_task, _get_completed_tasks, _get_tasks_by_closed_by
from api.actions.task import _close_task
from api.actions.task import _get_task_by_id
from api.actions.task import _update_task
from api.actions.task import _get_tasks_by_created_for
from api.actions.task import check_user_permissions_for_close_task

from api.actions.auth import get_current_user_from_token

from api.schemas import CloseTaskResponse, ShowCompletedTask, TaskCreate, ShowTask, UpdateTask, UpdatedTaskResponse
from db.models import User
from db.session import get_db

logger = getLogger(__name__)

task_router = APIRouter()

@task_router.post("/create_task/", response_model=ShowTask)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    try:
        return await _create_new_task(task, db, current_user)
    except IntegrityError as err:
            logger.error(err)
            raise HTTPException(status_code=503, detail=f"Database error: {err}")


@task_router.delete("/close_task/", response_model=CloseTaskResponse)
async def close_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> CloseTaskResponse:
    task_for_deletion = await _get_task_by_id(task_id, db)
    if task_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f"Task with id {task_id} not found."
        )
    #TODO: СРАВНИВАТЬ КООРДИНАТЫ И ДОБАВИТЬ ЗАКРЫТИЕ ДЛЯ АДМИНА
    permission = await check_user_permissions_for_close_task(task_for_deletion, current_user, db)
    if not permission:
        raise HTTPException(
            status_code=400,
            detail="You are too far from dog to complete this task",
        )
    close_task_id = await _close_task(task_id, db, current_user)
    return CloseTaskResponse(close_task_id=close_task_id)

@task_router.put("/update_task/", response_model=UpdatedTaskResponse)
async def update_task(
    task_id: UUID,
    update_task: UpdateTask,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> UpdatedTaskResponse:
    updated_task_params = update_task.dict(exclude_none=True)
    if updated_task_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for dog update info should be provided",
        )
    task_for_update = await _get_task_by_id(task_id, db)
    if task_for_update is None:
        raise HTTPException(
            status_code=404, detail=f"Task with id {task_id} not found."
        )
    if not check_user_permissions_for_close_task(
        target_task=task_for_update,
        current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")
    try:
        updated_task_id = await _update_task(updated_task_params, 
                                             task_id, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedTaskResponse(updated_task_id=updated_task_id)

@task_router.get("/get_task_by_id/", response_model=ShowTask)
async def get_task_by_id(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> ShowTask:
    task = await _get_task_by_id(task_id, db)
    if task is None:
        raise HTTPException(
            status_code=404, detail=f"Task with id {task_id} not found."
        )

    return ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_for=task.created_for,
            created_by=task.created_by,
            is_active=task.is_active,
        )    

@task_router.get("/get_tasks_by_created_for/", response_model=List[ShowTask])
async def get_tasks_by_created_for(
    created_for: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> List[ShowTask]:
    tasks = await _get_tasks_by_created_for(created_for, db)
    if tasks == []:
        raise HTTPException(
            status_code=404, detail=f"Tasks with dog_id {created_for} not found."
        )
    return [
        ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_for=task.created_for,
            created_by=task.created_by,
            is_active=task.is_active,
        ) for task in tasks
    ]

@task_router.get("/get_completed_tasks/", response_model=List[ShowCompletedTask])
async def get_completed_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> List[ShowCompletedTask]:
    tasks = await _get_completed_tasks(db)
    if tasks == []:
        raise HTTPException(
            status_code=404, detail='Have no completed tasks'
        )
    return [ShowCompletedTask(
        task_id=task.task_id,
        description=task.description,
        created_by=task.created_by,
        closed_by=task.closed_by,
        created_for=task.created_for,
    ) for task in tasks]

@task_router.get("/all_completed_tasks/", response_model=List[ShowCompletedTask])
async def get_completed_tasks_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> List[ShowCompletedTask]:
    tasks = await _get_tasks_by_closed_by(user_id, db)
    if not tasks:
        raise HTTPException(status_code=404, detail="No completed tasks found")
    return [ShowCompletedTask(
        task_id=task.task_id,
        description=task.description,
        created_by=task.created_by,
        closed_by=task.closed_by,
        created_for=task.created_for,
    ) for task in tasks]