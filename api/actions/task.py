from typing import List, Union
from uuid import UUID

from api.schemas import ShowTask
from api.schemas import TaskCreate

from db.dals import TaskDAL

from db.models import Task
from db.models import User


async def _create_new_task(body: TaskCreate, session, current_user: User) -> ShowTask:
    async with session.begin():
        task_dal = TaskDAL(session)
        task = await task_dal.create_task(
            description=body.description,
            created_for=body.created_for,
            created_by=current_user.user_id,
        )
        return ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_by=task.created_by,
            created_for=body.created_for,
            is_active=task.is_active,
        )

async def _delete_task(task_id: UUID, session) -> Union[UUID, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        updated_task_id = await task_dal.update_task(
            task_id=task_id, is_active=False
        )
        return updated_task_id

async def _update_task(updated_task_params: dict, task_id: UUID, session) -> Union[UUID, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        task = await task_dal.get_task_by_id(task_id)
        if task and task.is_active:
            updated_task_id = await task_dal.update_task(
                task_id=task_id, **updated_task_params
            )
            return updated_task_id
        return None

async def _get_task_by_id(task_id: UUID, session) -> Union[Task, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        task = await task_dal.get_task_by_id(
            task_id=task_id,
        )
        if task and task.is_active:
            return task
        return None

async def _get_tasks_by_created_for(created_for: UUID, session) -> List[Task]:
    async with session.begin():
        task_dal = TaskDAL(session)
        tasks = await task_dal.get_tasks_by_created_for(
            created_for=created_for,
        )
        return [task for task in tasks if task.is_active]