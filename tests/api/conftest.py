import pytest
from mixer.backend.flask import mixer
import megaqc.user.models as user_models
from tests import factories


# @pytest.fixture('function')
# def mix(app):
#     mixer.init_app(app)
#     return mixer


@pytest.yield_fixture('function')
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture('function')
def token(db):
    user = factories.UserFactory(is_admin=False)
    db.session.add(user)
    return user.api_token


@pytest.fixture('function')
def admin_token(db):
    user = factories.UserFactory(is_admin=True)
    db.session.add(user)
    return user.api_token


@pytest.fixture()
def session(db):
    sess = db.session
    return sess
