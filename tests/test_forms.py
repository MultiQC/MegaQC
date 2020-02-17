# -*- coding: utf-8 -*-
"""
Test forms.
"""
import pytest
from megaqc.public.forms import LoginForm
from megaqc.user.forms import RegisterForm
from tests.factories import UserFactory


@pytest.fixture()
def user_attrs():
    return UserFactory.build()


class TestRegisterForm:
    """
    Register form.
    """

    def test_validate_user_already_registered(self, user, user_attrs):
        """
        Enter username that is already registered.
        """
        form = RegisterForm(
            username=user.username,
            email=user_attrs.email,
            first_name=user_attrs.first_name,
            last_name=user_attrs.last_name,
            password="password",
            confirm="password",
        )

        assert form.validate() is False
        assert "Username already registered" in form.username.errors

    def test_validate_email_already_registered(self, user, user_attrs):
        """
        Enter email that is already registered.
        """
        form = RegisterForm(
            username=user_attrs.username,
            email=user.email,
            first_name=user_attrs.first_name,
            last_name=user_attrs.last_name,
            password="password",
            confirm="password",
        )

        assert form.validate() is False
        assert "Email already registered" in form.email.errors

    def test_validate_success(self, user_attrs, app):
        """
        Register with success.
        """
        form = RegisterForm(
            username=user_attrs.username,
            email=user_attrs.email,
            first_name=user_attrs.first_name,
            last_name=user_attrs.last_name,
            password="password",
            confirm="password",
        )
        assert form.validate() is True


class TestLoginForm:
    """
    Login form.
    """

    def test_validate_success(self, user):
        """
        Login successful.
        """
        user.set_password("example")
        user.save()
        form = LoginForm(username=user.username, password="example")
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_username(self, db):
        """
        Unknown username.
        """
        form = LoginForm(username="unknown", password="example")
        assert form.validate() is False
        assert "Unknown username" in form.username.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """
        Invalid password.
        """
        user.set_password("example")
        user.save()
        form = LoginForm(username=user.username, password="wrongpassword")
        assert form.validate() is False
        assert "Invalid password" in form.password.errors

    def test_validate_inactive_user(self, user):
        """
        Inactive user.
        """
        user.active = False
        user.set_password("example")
        user.save()
        # Correct username and password, but user is not activated
        form = LoginForm(username=user.username, password="example")
        assert form.validate() is False
        assert "User not activated" in form.username.errors
