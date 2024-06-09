import json
from uuid import uuid4
from conftest import create_test_auth_headers_for_user
from db.models import PortalRole

import pytest

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
        "/dog/create_dog", 
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
        "/dog/create_dog", 
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
        "/dog/create_dog", 
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
        "/dog/create_dog", 
        data=json.dumps(dog_data_for_creation),
        headers=create_test_auth_headers_for_user(user_data["email"])
        )
    data_from_resp = resp.json()
    assert resp.status_code == expected_status_code
    assert data_from_resp == expected_detail