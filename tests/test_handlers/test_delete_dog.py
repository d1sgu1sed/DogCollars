import pytest
from uuid import uuid4

from db.models import PortalRole

from conftest import create_test_auth_headers_for_user

async def test_delete_dog(client, create_dog_in_database, get_dog_from_database, create_user_in_database):
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
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={dog_data['dog_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_dog_id": str(dog_data["dog_id"])}
    dogs_from_db = await get_dog_from_database(dog_data["dog_id"])
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data["name"]
    assert dog_from_db["gender"] == dog_data["gender"]
    assert dog_from_db["is_active"] is False
    assert dog_from_db["dog_id"] == dog_data["dog_id"]

async def test_delete_dog_not_found(client, create_dog_in_database, create_user_in_database):
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
    dog_data_for_database = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    dog_data = {
        "dog_id": uuid4(),
        "name": "Max",
        "gender": "female",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data_for_database)
    await create_dog_in_database(**dog_data)
    id_not_exists_dog = uuid4()
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={id_not_exists_dog}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    assert resp.json() == {
        "detail": f"Dog with id {id_not_exists_dog} not found."
    }

async def test_delete_dog_id_validation_error(client, create_dog_in_database, create_user_in_database):
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
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    resp = client.delete(
        "/dog/delete_dog/?dog_id=123",
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

async def test_delete_dog_bad_cred(client, create_dog_in_database, create_user_in_database):
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
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    dog_id = uuid4()
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={dog_id}",
        headers=create_test_auth_headers_for_user(user_data["email"] + "a"),
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}

async def test_delete_dog_unauth(client, create_dog_in_database, create_user_in_database):
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
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    dog_id = uuid4()
    bad_auth_headers = create_test_auth_headers_for_user(user_data["email"])
    bad_auth_headers["Authorization"] += "a"
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={dog_id}",
        headers=bad_auth_headers,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}

async def test_delete_dog_no_jwt(client, create_dog_in_database, create_user_in_database):
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
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    dog_id = uuid4()
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={dog_data['dog_id']}",
        
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}

@pytest.mark.parametrize(
    "user_role_list",
    [
        [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
    ],
)
async def test_delete_dog_by_privilege_roles(
    client, create_dog_in_database, get_dog_from_database, user_role_list, create_user_in_database, 
):
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
    dog_data_for_deletion = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": user_data["user_id"],
        "is_active": True,
    }
    await create_dog_in_database(**dog_data_for_deletion)
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={dog_data_for_deletion['dog_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_dog_id": str(dog_data_for_deletion["dog_id"])}
    dogs_from_db = await get_dog_from_database(dog_data_for_deletion["dog_id"])
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data_for_deletion["name"]
    assert dog_from_db["gender"] == dog_data_for_deletion["gender"]
    assert dog_from_db["is_active"] is False
    assert dog_from_db["dog_id"] == dog_data_for_deletion["dog_id"]

@pytest.mark.parametrize(
    "dog_for_deletion, user_who_delete, expected_status_code",
    [
        (
            {
                "dog_id": uuid4(),
                "name": "Buddy",
                "gender": "male",
                "created_by": uuid4(),
                "is_active": True,
            },
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": [PortalRole.ROLE_PORTAL_USER],
            },
            403
        ),
        (
            {
                "dog_id": uuid4(),
                "name": "Buddy",
                "gender": "male",
                "created_by": uuid4(),
                "is_active": True,
            },
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": [PortalRole.ROLE_PORTAL_ADMIN],
            },
            200
        ),
        (
            {
                "dog_id": uuid4(),
                "name": "Buddy",
                "gender": "male",
                "created_by": uuid4(),
                "is_active": True,
            },
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": [PortalRole.ROLE_PORTAL_SUPERADMIN],
            },
            200
        )
    ],
)
async def test_delete_another_dog(
    client,
    create_dog_in_database,
    create_user_in_database,
    dog_for_deletion,
    user_who_delete,
    expected_status_code,
):
    await create_dog_in_database(**dog_for_deletion)
    await create_user_in_database(**user_who_delete)
    resp = client.delete(
        f"/dog/delete_dog/?dog_id={dog_for_deletion['dog_id']}",
        headers=create_test_auth_headers_for_user(user_who_delete["email"]),
    )
    assert resp.status_code == expected_status_code

