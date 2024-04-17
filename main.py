from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from sqlalchemy import Column, Boolean, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import settings
from sqlalchemy.dialects.postgresql import UUID
import uuid
import re
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import validator


#############################
# блок взаимодействия с бд
#############################

engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

#############################
# блок c моделью бд
#############################

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True) #удален пользователь или нет

#############################
# взаимодействия с пользователями
#############################

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name:str, surname:str, email:str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

#############################
# блок с API моделями
##########################

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

class TuneModel(BaseModel):
    class Config:
        orm_mode = True

class ShowUser(TuneModel): #ответ на запрос пользователя
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool

class UserCreate(BaseModel): #запрос
    name: str
    surname: str
    email: EmailStr

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Имя должно состоять только из букв!"
            )
        return value
    
    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Фамилия должна состоять только из букв!"
            )
        return value
    
#############################
# блок с API ROUTES
#############################

app = FastAPI(title="MobileDogs_K_and_S")

user_router = APIRouter()

async def _create_new_user(body: UserCreate) -> ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )
        
@user_router.post("/", response_model=ShowUser) # менеджер всех путей
async def create_user(body: UserCreate) -> ShowUser:
    return await _create_new_user(body)

main_api_router = APIRouter() # главный router

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)