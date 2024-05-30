import json
from uuid import uuid4
from conftest import create_test_auth_headers_for_user
from db.models import PortalRole

import pytest

async def test_create_user(client, get_user_from_database):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "password": "SamplePass1!",
    }
    resp = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_create_user_duplicate_email_error(client, get_user_from_database):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "password": "SamplePass1!",
    }
    user_data_same = {
        "name": "Petr",
        "surname": "Petrov",
        "email": "lol@kek.com",
        "password": "SamplePass1!",
    }
    resp = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]
    resp = client.post("/user/", data=json.dumps(user_data_same))
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )


@pytest.mark.parametrize(
    "user_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "surname"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "password"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        ),
        (
            {"name": 123, "surname": 456, "email": "lol"},
            422,
            {"detail": "Name should contains only letters"},
        ),
        (
            {"name": "Nikolai", "surname": 456, "email": "lol"},
            422,
            {"detail": "Surname should contains only letters"},
        ),
        (
            {"name": "Nikolai", "surname": "Sviridov", "email": "lol"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    },
                    {
                        "loc": ["body", "password"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        ),
    ],
)
async def test_create_user_validation_error(
    client, user_data_for_creation, expected_status_code, expected_detail
):
    resp = client.post("/user/", data=json.dumps(user_data_for_creation))
    data_from_resp = resp.json()
    assert resp.status_code == expected_status_code
    assert data_from_resp == expected_detail

# ------------------------------------------------- #

async def test_create_dog(client, get_dog_from_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "name": "Jack",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
    }
    resp = client.post(
        "/dog/", 
        data=json.dumps(dog_data),
        headers=create_test_auth_headers_for_user(user_data["email"]),
        )
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == dog_data["name"]
    assert data_from_resp["gender"] == dog_data["gender"]
    assert data_from_resp["is_active"] is True
    dogs_from_db = await get_dog_from_database(data_from_resp["dog_id"])
    assert len(dogs_from_db) == 1
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data["name"]
    assert dog_from_db["gender"] == dog_data["gender"]
    assert dog_from_db["is_active"] is True
    assert str(dog_from_db["dog_id"]) == data_from_resp["dog_id"]

async def test_create_dog_duplicate_name_error(client, get_dog_from_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    dog_data = {
        "name": "Jack",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
    }
    dog_data_same = {
        "name": "Jack",
        "gender": "female",
        "created_by": str(user_data["user_id"]),
    }
    await create_user_in_database(**user_data)
    resp = client.post(
        "/dog/", 
        data=json.dumps(dog_data),
        headers=create_test_auth_headers_for_user(user_data["email"])
        )
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == dog_data["name"]
    assert data_from_resp["gender"] == dog_data["gender"]
    assert data_from_resp["is_active"] is True
    dogs_from_db = await get_dog_from_database(data_from_resp["dog_id"])
    assert len(dogs_from_db) == 1
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data["name"]
    assert dog_from_db["gender"] == dog_data["gender"]
    assert dog_from_db["is_active"] is True
    assert str(dog_from_db["dog_id"]) == data_from_resp["dog_id"]
    
    resp = client.post(
        "/dog/", 
        data=json.dumps(dog_data_same),
        headers=create_test_auth_headers_for_user(user_data["email"])
        )
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "dogs_name_key"'
        in resp.json()["detail"]
    )

@pytest.mark.parametrize(
    "dog_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "gender"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        ),
        (
            {"name": "123", "gender": "456"},
            422,
            {
                "detail": 'Name and gender should contain only letters'
            },
        ),
        (
            {"name": "Jack", "gender": "456"},
            422,
            {
                "detail": "Gender should be 'male' or 'female'"
            },
        ),
    ],
)
async def test_create_dog_validation_error(
    client, dog_data_for_creation, expected_status_code, expected_detail, create_user_in_database
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)
    resp = client.post(
        "/dog/", 
        data=json.dumps(dog_data_for_creation),
        headers=create_test_auth_headers_for_user(user_data["email"])
        )
    data_from_resp = resp.json()
    assert resp.status_code == expected_status_code
    assert data_from_resp == expected_detail