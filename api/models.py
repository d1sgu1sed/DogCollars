import uuid
import re

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import validator

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

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value