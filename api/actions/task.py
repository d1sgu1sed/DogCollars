from typing import Union
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
            created_by=current_user.user_id,
        )
        return ShowTask(
            task_id=task.task_id,
            description=task.description,
            created_by=task.created_by,
            is_active=task.is_active,
        )

async def _delete_task(task_id: UUID, session) -> Union[UUID, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        deleted_task_id = await task_dal.delete_task(
            task_id=task_id,
        )
        return deleted_task_id

async def _update_task(updated_task_params: dict, task_id: UUID, session) -> Union[UUID, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        updated_task_id = await task_dal.update_task(
            task_id=task_id, **updated_task_params
        )
        return updated_task_id

async def _get_task_by_id(task_id: UUID, session) -> Union[Task, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        task = await task_dal.get_task_by_id(
            task_id=task_id,
        )
        return task