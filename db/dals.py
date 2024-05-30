from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import PortalRole
from db.models import User
from db.models import Dog

##########################
# БЛОК ИНТЕРАКЦИЙ С DALS #
##########################


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        hashed_password: str,
        roles: list[PortalRole],
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]
        
class DogDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_dog(
        self,
        name: str,
        gender: str,
        created_by: UUID,) -> Dog:
        new_dog = Dog(
            name=name,
            gender=gender,
            created_by=created_by,
        )
        self.db_session.add(new_dog)
        await self.db_session.flush()
        return new_dog

    async def delete_dog(self, dog_id: UUID) -> Union[UUID, None]:
        query = (
            update(Dog)
            .where(and_(Dog.dog_id == dog_id, Dog.is_active == True))
            .values(is_active=False)
            .returning(Dog.dog_id)
        )
        res = await self.db_session.execute(query)
        deleted_dog_id_row = res.fetchone()
        if deleted_dog_id_row is not None:
            return deleted_dog_id_row[0]

    async def get_dog_by_id(self, dog_id: UUID) -> Union[Dog, None]:
        query = select(Dog).where(Dog.dog_id == dog_id)
        res = await self.db_session.execute(query)
        dog_row = res.fetchone()
        if dog_row is not None:
            return dog_row[0]
        
    async def get_dog_by_name(self, name: str) -> Union[Dog, None]:
        query = select(Dog).where(Dog.name == name)
        res = await self.db_session.execute(query)
        dog_row = res.fetchone()
        if dog_row is not None:
            return dog_row[0]

    async def update_dog(self, dog_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(Dog)
            .where(and_(Dog.dog_id == dog_id, Dog.is_active == True))
            .values(kwargs)
            .returning(Dog.dog_id)
        )
        res = await self.db_session.execute(query)
        update_dog_id_row = res.fetchone()
        if update_dog_id_row is not None:
            return update_dog_id_row[0]