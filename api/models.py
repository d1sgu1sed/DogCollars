import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator

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
    
class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID

class UpdatedUserResponce(BaseModel):
    updated_user_id: uuid.UUID
    