import pytest

from .utils import (
    find_factory,
    instance_pk,
    list_resource_endpoints,
    resource_from_endpoint,
    single_resource_endpoints,
    url_for,
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
    Test that each endpoint can only be accessed by the appropriate permission
    level.
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
    Test that each endpoint can only be accessed by the appropriate permission
    level.
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
