from logging import getLogger
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.dog import _create_new_dog
from api.actions.dog import _delete_dog
from api.actions.dog import _get_dog_by_id
from api.actions.dog import _update_dog
from api.actions.dog import check_user_permissions_for_dog_delete

from api.actions.auth import get_current_user_from_token

from api.schemas import DogCreate, UpdatedDogResponse, UpdateDogRequest, DeleteDogResponse, ShowDog, ShowCoords
from db.models import User
from db.session import get_db

logger = getLogger(__name__)

dog_router = APIRouter()

@dog_router.post("/", response_model=ShowDog)
async def create_dog(
    body: DogCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)) -> ShowDog:
    try:
        return await _create_new_dog(body, db, current_user)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

@dog_router.delete("/", response_model=DeleteDogResponse)
async def delete_dog(
    dog_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> DeleteDogResponse:
    dog_for_deletion = await _get_dog_by_id(dog_id, db)
    if dog_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f"Dog with id {dog_id} not found."
        )
    if not check_user_permissions_for_dog_delete(
        target_dog=dog_for_deletion,
        current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")
    deleted_dog_id = await _delete_dog(dog_id, db)
    if deleted_dog_id is None:
        raise HTTPException(
            status_code=404, detail=f"Dog with id {dog_id} not found."
        )
    return DeleteDogResponse(deleted_dog_id=deleted_dog_id)

@dog_router.patch("/", response_model=UpdatedDogResponse)
async def update_dog_by_id(
    dog_id: UUID,
    body: UpdateDogRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> UpdatedDogResponse:
    updated_dog_params = body.dict(exclude_none=True)
    if updated_dog_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for dog update info should be provided",
        )
    dog_for_update = await _get_dog_by_id(dog_id, db)
    if dog_for_update is None:
        raise HTTPException(
            status_code=404, detail=f"Dog with id {dog_id} not found."
        )
    if not check_user_permissions_for_dog_delete(
        target_dog=dog_for_update,
        current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")
    try:
        updated_dog_id = await _update_dog(
            updated_dog_params=updated_dog_params, session=db, dog_id=dog_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedDogResponse(updated_dog_id=updated_dog_id)

@dog_router.get("/", response_model=ShowDog)
async def get_dog_by_id(
    dog_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> ShowDog:
    dog = await _get_dog_by_id(dog_id, db)
    if dog is None:
        raise HTTPException(
            status_code=404, detail=f"Dog with id {dog_id} not found."
        )
    return dog


@dog_router.patch("/location", response_model=ShowCoords)
async def update_dog_location(
    dog_id: UUID,
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> ShowDog:
    dog_for_update = await _get_dog_by_id(dog_id, db)
    if dog_for_update is None:
        raise HTTPException(
            status_code=404, detail=f"Dog with id {dog_id} not found."
        )
    if not check_user_permissions_for_dog_delete(
        target_dog=dog_for_update,
        current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")
    updated_dog_params = {
        "latitude": latitude,
        "longitude": longitude,
    }
    try:
        updated_dog_id = await _update_dog(
            updated_dog_params=updated_dog_params, session=db, dog_id=dog_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return ShowCoords(dog_id=dog_for_update.dog_id, name=dog_for_update.name, latitude=updated_dog_params["latitude"], longitude=updated_dog_params["longitude"])

@dog_router.get("/location", response_model=ShowCoords)
async def get_dog_location(
    dog_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> ShowCoords:
    dog = await _get_dog_by_id(dog_id, db)
    if dog is None:
        raise HTTPException(
            status_code=404, detail=f"Dog with id {dog_id} not found."
        )
    if dog.latitude is None:
        dog.latitude = 0
    if dog.longitude is None:
        dog.longitude = 0
    return ShowCoords(dog_id=dog.dog_id, name=dog.name, latitude=dog.latitude, longitude=dog.longitude)