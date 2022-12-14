import pytest
from flask import request
from flask.testing import FlaskClient

from tests import factories


@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as c:
        c: FlaskClient
        yield c


@pytest.fixture(scope="function")
def token(db: str):
    user = factories.UserFactory(is_admin=False)
    db.session.add(user)
    db.session.commit()
    return user.api_token


@pytest.fixture(scope="function")
def admin_token(db) -> str:
    user = factories.UserFactory(is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user.api_token
