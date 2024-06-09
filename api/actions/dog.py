from typing import Union
from uuid import UUID

from fastapi import HTTPException

from db.dals import DogDAL, TaskDAL
from db.models import User
from db.models import PortalRole
from db.models import Dog
from api.schemas import ShowDog
from api.schemas import DogCreate

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

async def _delete_dog(dog_id, session) -> UUID:
    async with session.begin():
        dog_dal = DogDAL(session)
        deleted_dog_id = await dog_dal.delete_dog(
            dog_id=dog_id,
        )
        return deleted_dog_id


async def _update_dog(updated_dog_params: dict, dog_id: UUID, session) -> UUID:
    async with session.begin():
        dog_dal = DogDAL(session)
        task_dal = TaskDAL(session)

        tasks = await task_dal.get_tasks_by_created_for(dog_id)
        for task in tasks:
            await task_dal.delete_task(task.task_id)
        
        updated_dog_id = await dog_dal.update_dog(
            dog_id=dog_id, **updated_dog_params
        )
        return updated_dog_id


async def _get_dog_by_id(dog_id, session) -> Dog:
    async with session.begin():
        dog_dal = DogDAL(session)
        dog = await dog_dal.get_dog_by_id(
            dog_id=dog_id,
        )
        if dog is not None:
            return dog 
        
async def _get_dog_by_name(name: str, session) -> UUID:
    async with session.begin():
        dog_dal = DogDAL(session)
        dog_id = await dog_dal.get_dog_by_name(name)
        return dog_id

        
def check_user_permissions_for_dog(target_dog: Dog, current_user: User) -> bool:
    if len(current_user.roles) == 1 and PortalRole.ROLE_PORTAL_USER in current_user.roles:
        if target_dog.created_by != current_user.user_id:
            raise HTTPException(
                status_code=403, detail="Common user can't delete this dog."
            )
    return True

def check_superadmin(current_user: User) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        return True
    return False
