from typing import List, Union
from uuid import UUID
# from geopy.distance import geodesic

from numpy import sin, cos, arccos, pi, round
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db

from fastapi import HTTPException
from fastapi import Depends
from api.schemas import ShowTask
from api.schemas import TaskCreate

from db.dals import TaskDAL

from db.models import Task
from db.models import PortalRole
from db.models import User

from api.actions.dog import _get_dog_by_id

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

async def _close_task(task_id: UUID, session, current_user: User) -> Union[UUID, None]:
    async with session.begin():
        task_dal = TaskDAL(session)
        updated_task_id = await task_dal.close_task(
            task_id=task_id, 
            current_user=current_user
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

async def _get_completed_tasks(session) -> List[Task]:
    async with session.begin():
        task_dal = TaskDAL(session)
        tasks = await task_dal.get_completed_tasks()
        return tasks
    
async def _get_tasks_by_closed_by(closed_by: UUID, session: AsyncSession) -> List[Task]:
    async with session.begin():
        task_dal = TaskDAL(session)
        tasks = await task_dal.get_tasks_by_closed_by(closed_by)
        return tasks
    
async def check_user_permissions_for_close_task(target_task: Task, current_user: User, db: AsyncSession = Depends(get_db)) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    # check admins roles
    if {
        PortalRole.ROLE_PORTAL_ADMIN,
        PortalRole.ROLE_PORTAL_SUPERADMIN,
    }.intersection(current_user.roles):
        return True
    
    dog_from_task = await _get_dog_by_id(target_task.created_for, db)
    # ПРОВЕРКА НА КООРДИНАТЫ
    dog_coords = (dog_from_task.latitude, dog_from_task.longitude)
    user_coords = (current_user.latitude, current_user.longitude)
    print(dog_coords)
    print(user_coords)
    distance = get_distance_between_points(dog_from_task.latitude, dog_from_task.longitude,
                                           current_user.latitude, current_user.longitude)
    print(distance)

    if(distance <= 0.1):
        return True

    return False

def rad2deg(radians):
    degrees = radians * 180 / pi
    return degrees

def deg2rad(degrees):
    radians = degrees * pi / 180
    return radians

def get_distance_between_points(latitude1, longitude1, latitude2, longitude2, unit = 'kilometers'):
    theta = longitude1 - longitude2
    print(theta)
    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(latitude1)) * sin(deg2rad(latitude2))) + 
            (cos(deg2rad(latitude1)) * cos(deg2rad(latitude2)) * cos(deg2rad(theta)))
        )
    )
    
    if unit == 'miles':
        return round(distance, 4)
    if unit == 'kilometers':
        return round(distance * 1.609344, 4)
