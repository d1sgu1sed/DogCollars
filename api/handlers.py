from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from api.models import UserCreate, ShowUser
from db.dals import UserDAL
from db.session import get_db
import uuid
import re

from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UserCreate
from db.models import User

from fastapi import HTTPException

user_router = APIRouter()

async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
            )
            return ShowUser(
                user_id = user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )
        
@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)

@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return DeleteUserResponse(deleted_user_id=deleted_user_id)




