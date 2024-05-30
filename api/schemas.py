import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator

##############################
# БЛОК РАБОТЫ С API МОДЕЛЯМИ #
##############################

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class ShowUser(TunedModel):
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


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

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

class Token(BaseModel):
    access_token: str
    token_type: str

# ------------------------------------------------------------------------------- #   

class ShowDog(TunedModel):
    dog_id: uuid.UUID
    name: str
    gender: str
    is_active: bool

class ShowCoords(TunedModel):
    dog_id: uuid.UUID
    name: str
    longitude: float
    latitude: float


class DogCreate(BaseModel):
    name: str
    gender: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name and gender should contain only letters"
            )
        return value

    @validator("gender")
    def validate_gender(cls, value):
        if value not in ["male", "female"]:
            raise HTTPException(
                status_code=422, detail="Gender should be 'male' or 'female'"
            )
        return value



class DeleteDogResponse(BaseModel):
    deleted_dog_id: uuid.UUID


class UpdatedDogResponse(BaseModel):
    updated_dog_id: uuid.UUID


class UpdateDogRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    gender: Optional[str]

    @validator("name", "gender")
    def validate_name_or_gender(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name and gender should contain only letters"
            )
        return value

    @validator("gender")
    def validate_gender(cls, value):
        if value not in ["male", "female"]:
            raise HTTPException(
                status_code=422, detail="Gender should be 'male' or 'female'"
            )
        return value