import pytest
from flask import Flask
from marshmallow import EXCLUDE

from megaqc.rest_api.schemas import UserSchema
from megaqc.user.models import User
from tests.factories import UserFactory

from .utils import (
    dump_only_fields,
    find_factory,
    instance_pk,
    list_resource_endpoints,
    resource_from_endpoint,
    single_resource_endpoints,
    url_for,
)


def raise_response(resp: Flask.response_class):
    if not str(resp.status_code).startswith("2"):
        raise Exception(
            "Request failed with status {} and body {}".format(
                resp.status_code, resp.data
            )
        )


@pytest.mark.parametrize(
    "endpoint", set(single_resource_endpoints) - {"rest_api.report"}
)
@pytest.mark.parametrize(
    "method,success",
    [
        ["GET", True],
        ["PATCH", False],
        ["DELETE", False],
    ],
)
def test_single_resource_permissions(
    endpoint, method, success, token, admin_token, session, client, app
):
    """
    Test that each endpoint can only be accessed by the appropriate permission level.
    """
    resource = resource_from_endpoint(app, endpoint)
    model = resource.data_layer["model"]
    factory = find_factory(model)

    # Construct an instance of the model
    instance = factory()
    session.commit()

    # Do the request
    pk = instance_pk(instance)[1]
    url = url_for(endpoint, id=pk)

    # Check the request had the expected status, given that we're acting as a regular user
    rv = client.open(
        url,
        method=method,
        headers={"access_token": token, "Content-Type": "application/json"},
    )
    # Since we only care about access, we don't check if the request succeeded or not, just if it didn't 403
    assert (rv.status_code != 403) == success

    # Check the request worked, given that we're now an admin
    rv = client.open(
        url,
        method=method,
        headers={"access_token": admin_token, "Content-Type": "application/json"},
    )
    assert rv.status_code != 403


@pytest.mark.parametrize(
    # These two have unusual permissions
    "endpoint",
    set(list_resource_endpoints) - {"rest_api.uploadlist", "rest_api.userlist"},
)
@pytest.mark.parametrize(
    "method,success",
    [
        ["GET", True],
        ["POST", False],
    ],
)
def test_many_resources_permissions(
    endpoint, method, success, session, client, admin_token, token
):
    """
    Test that each endpoint can only be accessed by the appropriate permission level.
    """
    # Do the request
    url = url_for(endpoint)

    # Check the request had the expected status, given that we're acting as a regular user
    rv = client.open(
        url,
        method=method,
        headers={"access_token": token, "Content-Type": "application/json"},
    )
    # Since we only care about access, we don't check if the request succeeded or not, just if it didn't 403
    assert (rv.status_code != 403) == success

    # Check the request worked, given that we're now an admin
    rv = client.open(
        url,
        method=method,
        headers={"access_token": admin_token, "Content-Type": "application/json"},
    )
    assert rv.status_code != 403


@pytest.mark.parametrize("strict", [True, False])
def test_active_inactive(session, strict, app, client):
    """
    The first user to register should be an activated admin, and subsequent users should
    be inactive and regular users.
    """
    app.config["USER_REGISTRATION_APPROVAL"] = strict

    # Non-admins aren't allowed to specify these fields
    dump_only = dump_only_fields(UserSchema) + ["admin", "active", "salt", "api_token"]
    req_schema = UserSchema(many=False, use_links=False, exclude=dump_only)
    res_schema = UserSchema(many=False, unknown=EXCLUDE)
    url = url_for("rest_api.userlist")
    first = UserFactory.build()
    second = UserFactory.build()

    # The first created user should be an active admin
    first_res: Flask.response_class = client.post(path=url, json=req_schema.dump(first))
    raise_response(first_res)
    first_model: dict = res_schema.load(first_res.json)
    assert first_model["active"]
    assert first_model["is_admin"]

    # The second and subsequent users should be active only if it's not in strict mode
    second_res: Flask.response_class = client.post(
        path=url, json=req_schema.dump(second)
    )
    raise_response(second_res)
    second_model: dict = res_schema.load(second_res.json)
    assert second_model["active"] != strict
    assert not second_model["is_admin"]
