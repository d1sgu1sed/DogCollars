import json
import pytest
from httpx import AsyncClient
from uuid import uuid4
from fastapi import status
from conftest import create_test_auth_headers_for_user

from db.models import PortalRole

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, create_user_in_database, create_dog_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "description": "Test task",
        "created_for": str(dog_data["dog_id"]),
    }
    response = client.post("/task/create_task/", json=task_data, headers=create_test_auth_headers_for_user(user_data["email"]))
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["description"] == task_data["description"]
    assert data["created_for"] == task_data["created_for"]
    assert data["created_by"] == str(user_data["user_id"])
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_close_task(client: AsyncClient, create_user_in_database, create_dog_in_database, create_task_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": str(dog_data["dog_id"]),
        "created_by": dog_data["dog_id"],
        "closed_by": None,
        "is_active": True
    }
    await create_task_in_database(**task_data)
    response = client.delete(f"/task/close_task/?task_id={task_data['task_id']}", headers=create_test_auth_headers_for_user(user_data["email"]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["close_task_id"] == str(task_data["task_id"])

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, create_user_in_database, create_dog_in_database, create_task_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    await create_task_in_database(**task_data)
    task_data_updated = {
        "description": "Another test task"
    }
    response = client.put(
        f"/task/update_task/?task_id={task_data['task_id']}", 
        data=json.dumps(task_data_updated), 
        headers=create_test_auth_headers_for_user(user_data["email"]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["updated_task_id"] == str(task_data["task_id"])

@pytest.mark.asyncio
async def test_get_task_by_id(client: AsyncClient, create_user_in_database, create_dog_in_database, create_task_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    await create_task_in_database(**task_data)
    response = client.get(f"/task/get_task_by_id/?task_id={task_data['task_id']}", headers=create_test_auth_headers_for_user(user_data["email"]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["task_id"] == str(task_data["task_id"])
    assert data["description"] == task_data["description"]
    assert data["created_for"] == str(task_data["created_for"])
    assert data["created_by"] == str(task_data["created_by"])
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_get_tasks_by_created_for(client: AsyncClient, create_user_in_database, create_dog_in_database, create_task_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    await create_task_in_database(**task_data)
    response = client.get(f"/task/get_tasks_by_created_for/?created_for={task_data['created_for']}", headers=create_test_auth_headers_for_user(user_data["email"]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for t in data:
        assert t["created_for"] == str(task_data["created_for"])

@pytest.mark.asyncio
async def test_get_all_active_tasks(client: AsyncClient, create_user_in_database, create_dog_in_database, create_task_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    task_data2 = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    await create_task_in_database(**task_data)
    await create_task_in_database(**task_data2)
    response = client.get("/task/get_all_active_tasks/", headers=create_test_auth_headers_for_user(user_data["email"]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for t in data:
        assert t["is_active"] is True

@pytest.mark.asyncio
async def test_get_completed_tasks_by_user(client: AsyncClient, create_user_in_database, create_dog_in_database, create_task_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "Male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    task_data = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    task_data2 = {
        "task_id": uuid4(),
        "description": "Test task",
        "created_for": dog_data["dog_id"],
        "created_by": user_data["user_id"],
        "closed_by": None,
        "is_active": True
    }
    await create_task_in_database(**task_data)
    await create_task_in_database(**task_data2)
    client.delete(f"task/close_task/?task_id={task_data['task_id']}", headers=create_test_auth_headers_for_user(user_data["email"]))
    response = client.get(f"/task/all_completed_tasks/?user_id={user_data['user_id']}", headers=create_test_auth_headers_for_user(user_data["email"]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for t in data:
        assert t["closed_by"] == str(user_data['user_id'])
