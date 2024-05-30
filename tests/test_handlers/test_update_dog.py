import json
from uuid import uuid4

import pytest

from db.models import PortalRole
from conftest import create_test_auth_headers_for_user

@pytest.mark.parametrize(
    "user_roles, expected_status",
    [
        ([PortalRole.ROLE_PORTAL_SUPERADMIN], 200),
        ([PortalRole.ROLE_PORTAL_ADMIN], 200),
        ([PortalRole.ROLE_PORTAL_USER], 200),
        ([PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_SUPERADMIN], 200),
    ],
)
async def test_update_dog(
    client, create_dog_in_database, create_user_in_database, get_dog_from_database, user_roles, expected_status
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": user_roles,
    }
    await create_user_in_database(**user_data)
    
    dog_data = {
        "dog_id": uuid4(),  # Changed id to dog_id
        "name": "Buddy",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    dog_data_updated = {
        "name": "Max",
        "gender": "female"
    }
    await create_dog_in_database(**dog_data)
    resp = client.patch(
        f"/dog/?dog_id={dog_data['dog_id']}",  # Changed id to dog_id
        data=json.dumps(dog_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == expected_status
    if expected_status == 200:
        resp_data = resp.json()
        assert resp_data["updated_dog_id"] == str(dog_data["dog_id"])  # Changed id to dog_id
        dogs_from_db = await get_dog_from_database(dog_data["dog_id"])  # Changed id to dog_id
        dog_from_db = dict(dogs_from_db[0])
        assert dog_from_db["name"] == dog_data_updated["name"]
        assert dog_from_db["gender"] == dog_data_updated["gender"]
        assert dog_from_db["dog_id"] == dog_data["dog_id"]  # Changed id to dog_id


async def test_update_dog_check_one_is_updated(
    client, create_dog_in_database, create_user_in_database, get_dog_from_database
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
    dog_data_1 = {
        "dog_id": uuid4(),  # Changed id to dog_id
        "name": "Buddy",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    dog_data_2 = {
        "dog_id": uuid4(),  # Changed id to dog_id
        "name": "Charlie",
        "gender": "female",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    dog_data_3 = {
        "dog_id": uuid4(),  # Changed id to dog_id
        "name": "Rocky",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    dog_data_updated = {
        "name": "Max",
        "gender": "female",
        "created_by": str(user_data["user_id"]),
        "is_active": False,
    }
    for dog_data in [dog_data_1, dog_data_2, dog_data_3]:
        await create_dog_in_database(**dog_data)
    resp = client.patch(
        f"/dog/?dog_id={dog_data_1['dog_id']}",  # Changed id to dog_id
        data=json.dumps(dog_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_dog_id"] == str(dog_data_1["dog_id"])  # Changed id to dog_id
    dogs_from_db = await get_dog_from_database(dog_data_1["dog_id"])  # Changed id to dog_id
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data_updated["name"]
    assert dog_from_db["gender"] == dog_data_updated["gender"]
    assert dog_from_db["dog_id"] == dog_data_1["dog_id"]  # Changed id to dog_id

    # check other dogs that data has not been changed
    dogs_from_db = await get_dog_from_database(dog_data_2["dog_id"])  # Changed id to dog_id
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data_2["name"]
    assert dog_from_db["gender"] == dog_data_2["gender"]
    assert dog_from_db["dog_id"] == dog_data_2["dog_id"]  # Changed id to dog_id

    dogs_from_db = await get_dog_from_database(dog_data_3["dog_id"])  # Changed id to dog_id
    dog_from_db = dict(dogs_from_db[0])
    assert dog_from_db["name"] == dog_data_3["name"]
    assert dog_from_db["gender"] == dog_data_3["gender"]
    assert dog_from_db["dog_id"] == dog_data_3["dog_id"]  # Changed id to dog_id


@pytest.mark.parametrize(
    "dog_data_updated, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": "At least one parameter for dog update info should be provided"
            },
        ),
        ({"name": "123"}, 422, {"detail": "Name and gender should contain only letters"}),
        (
            {"gender": ""},
            422,
            {
                "detail": "Name and gender should contain only letters"
            },
        ),
        (
            {"name": ""},
            422,
            
                {'detail': [{'ctx': {'limit_value': 1}, 'loc': ['body', 'name'], 'msg': 'ensure this value has at least 1 characters', 'type': 'value_error.any_str.min_length'}]}
            ,
        ),
        (
            {"gender": "123"},
            422,
            {"detail": "Name and gender should contain only letters"}
        ),
    ],
)
async def test_update_dog_validation_error(
    client,
    create_dog_in_database,
    create_user_in_database,
    get_dog_from_database,
    dog_data_updated,
    expected_status_code,
    expected_detail,
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
    dog_data = {
        "dog_id": uuid4(),  # Changed id to dog_id
        "name": "Buddy",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/dog/?dog_id={dog_data['dog_id']}",  # Changed id to dog_id
        data=json.dumps(dog_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_update_dog_id_validation_error(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    dog_data = {
        "dog_id": uuid4(),  # Changed id to dog_id
        "name": "Buddy",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    await create_user_in_database(**user_data)
    dog_data_updated = {
        "name": "Max",
        "gender": "female",
        "is_active": False,
    }
    resp = client.patch(
        "/dog/?dog_id=123",
        data=json.dumps(dog_data_updated),
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


async def test_update_dog_not_found_error(client, create_dog_in_database, create_user_in_database):
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
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    await create_dog_in_database(**dog_data)
    dog_data_updated = {
        "name": "Max",
        "gender": "female",
    }
    dog_id = uuid4()
    resp = client.patch(
        f"/dog/?dog_id={dog_id}",  # Changed id to dog_id
        data=json.dumps(dog_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    resp_data = resp.json()
    assert resp_data == {"detail": f"Dog with id {dog_id} not found."}


async def test_update_dog_duplicate_name_error(client, create_dog_in_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_ADMIN],
    }
    dog_data_1 = {
        "dog_id": uuid4(),
        "name": "Buddy",
        "gender": "male",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    dog_data_2 = {
        "dog_id": uuid4(), 
        "name": "Max",
        "gender": "female",
        "created_by": str(user_data["user_id"]),
        "is_active": True,
    }
    dog_data_updated = {
        "name": dog_data_2["name"],
    }
    for dog_data in [dog_data_1, dog_data_2]:
        await create_dog_in_database(**dog_data)
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/dog/?dog_id={dog_data_1['dog_id']}",  
        data=json.dumps(dog_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "dogs_name_key"'
        in resp.json()["detail"]
    )
