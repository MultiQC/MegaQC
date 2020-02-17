import pytest
from flask_login import login_user
from pkg_resources import resource_stream

from megaqc.model import models
from megaqc.rest_api import schemas
from tests import factories
from flask_login import login_user


def test_current_user_session_working(session, token, app):
    """
    Test the current_user endpoint, using a valid session. This should work
    """
    # Create a user
    user = factories.UserFactory()
    session.add(user)
    session.commit()

    # Login with that user (we have to use a custom client here)
    with app.test_client(user=user) as client:
        rv = client.get('/rest_api/v1/users/current')

    # Check the request was successful
    assert rv.status_code == 200, rv.json

    # Validate the response
    schemas.UserSchema().validate(rv.json)


def test_current_user_session_invalid(session, client, token):
    """
    Test the current_user endpoint, using a valid session. This should work
    """
    # Create a user
    user = factories.UserFactory()
    session.add(user)
    session.commit()

    rv = client.get('/rest_api/v1/users/current')

    # Check the request was unauthorized
    assert rv.status_code == 401