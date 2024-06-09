import pytest
from uuid import uuid4
from conftest import create_test_auth_headers_for_user

async def test_get_dog(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": uuid4(),
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    resp = client.get(
        f"/dog/get_dog_by_id/?dog_id={dog_data['dog_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    dog_from_response = resp.json()
    assert dog_from_response["dog_id"] == str(dog_data["dog_id"])
    assert dog_from_response["name"] == dog_data["name"]
    assert dog_from_response["gender"] == dog_data["gender"]
    assert dog_from_response["is_active"] == dog_data["is_active"]

async def test_get_dog_id_validation_error(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": uuid4(),
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    resp = client.get(
        "/dog/get_dog_by_id/?dog_id=123",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "dog_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }

async def test_get_dog_not_found(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": uuid4(),
        "is_active": True,
    }
    dog_id_for_finding = uuid4()
    await create_dog_in_database(**dog_data)
    resp = client.get(
        f"/dog/get_dog_by_id/?dog_id={dog_id_for_finding}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"Dog with id {dog_id_for_finding} not found."}

async def test_get_dog_unauth_error(client, create_dog_in_database):
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": uuid4(),
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    resp = client.get(
        f"/dog/get_dog_by_id/?dog_id={dog_data['dog_id']}",
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}

async def test_get_dog_bad_cred(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    resp = client.get(
        f"/dog/get_dog_by_id/?dog_id={dog_data['dog_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"] + "a"),
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}

async def test_get_dog_unauth(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    dog_data = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    bad_auth_headers = create_test_auth_headers_for_user(user_data["email"])
    bad_auth_headers["Authorization"] += "a"
    resp = client.get(
        f"/dog/get_dog_by_id/?dog_id={dog_data['dog_id']}",
        headers=bad_auth_headers,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}
