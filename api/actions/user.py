from typing import Union
from uuid import UUID

from fastapi import HTTPException

from api.schemas import ShowUser
from api.schemas import UserCreate
from api.schemas import ShowDog
from api.schemas import DogCreate
from api.schemas import ShowTask
from api.schemas import TaskCreate
from db.dals import UserDAL
from db.dals import DogDAL
from db.dals import TaskDAL
from db.models import PortalRole
from db.models import User
from db.models import Dog
from db.models import Task
from hashing import Hasher


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
            roles=[
                PortalRole.ROLE_PORTAL_USER,
            ],
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id, session) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(
            user_id=user_id,
        )
        return deleted_user_id


async def _update_user(
    updated_user_params: dict, user_id: UUID, session
) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params
        )
        return updated_user_id


async def _get_user_by_id(user_id, session) -> Union[User, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user


def check_user_permissions(target_user: User, current_user: User) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    if target_user.user_id != current_user.user_id:
        # check admin role
        if not {
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN,
        }.intersection(current_user.roles):
            return False
        # check admin deactivate superadmin attempt
        if (
            PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
        # check admin deactivate admin attempt
        if (
            PortalRole.ROLE_PORTAL_ADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
    return True

# ----------------------------------------------------------------------- #

async def _create_new_dog(body: DogCreate, session, current_user: User) -> ShowDog:
    async with session.begin():
        dog_dal = DogDAL(session)
        dog = await dog_dal.create_dog(
            name=body.name,
            gender=body.gender,
            created_by=current_user.user_id,
        )
        return ShowDog(
            dog_id=dog.dog_id,
            name=dog.name,
            gender=dog.gender,
            created_by=dog.created_by,
            is_active=dog.is_active,
        )

async def _delete_dog(dog_id, session) -> Union[UUID, None]:
    async with session.begin():
        dog_dal = DogDAL(session)
        deleted_dog_id = await dog_dal.delete_dog(
            dog_id=dog_id,
        )
        return deleted_dog_id


async def _update_dog(updated_dog_params: dict, dog_id: UUID, session) -> Union[UUID, None]:
    async with session.begin():
        dog_dal = DogDAL(session)
        updated_dog_id = await dog_dal.update_dog(
            dog_id=dog_id, **updated_dog_params
        )
        return updated_dog_id


async def _get_dog_by_id(dog_id, session) -> Union[Dog, None]:
    async with session.begin():
        dog_dal = DogDAL(session)
        dog = await dog_dal.get_dog_by_id(
            dog_id=dog_id,
        )
        if dog is not None:
            return dog 
        
def check_user_permissions_for_dog_delete(target_dog: Dog, current_user: User) -> bool:
    if len(current_user.roles) == 1 and PortalRole.ROLE_PORTAL_USER in current_user.roles:
        if target_dog.created_by != current_user.user_id:
            raise HTTPException(
                status_code=403, detail="Common user can't delete this dog."
            )
    return True


#------------------------------------------------------------#

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
