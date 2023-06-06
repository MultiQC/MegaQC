import os
from enum import IntEnum, auto
from functools import wraps
from uuid import uuid4

from flapison.exceptions import JsonApiException
from flask import abort, request
from flask.globals import current_app

from megaqc.user.models import User


def get_upload_dir():
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    return upload_dir


def get_unique_filename():
    dir = get_upload_dir()
    while True:
        proposed = os.path.join(dir, str(uuid4()))
        if not os.path.exists(proposed):
            return proposed


class Permission(IntEnum):
    NONUSER = auto()
    USER = auto()
    ADMIN = auto()


def api_perms(min_level: Permission = Permission.NONUSER):
    """
    Adds a "user" and "permission" kwarg to the view function. Also verifies a minimum
    permissions level.

    :param min_level: If provided, this is the minimum permission level
        required by this endpoint
    """

    def wrapper(function):
        @wraps(function)
        def user_wrap_function(*args, **kwargs):
            extra = None
            if not request.headers.has_key("access_token"):
                perms = Permission.NONUSER
                user = None
                extra = "No access token provided. Please add a header with the name 'access_token'."
            else:
                user = User.query.filter_by(
                    api_token=request.headers.get("access_token")
                ).first()
                if not user:
                    perms = Permission.NONUSER
                    extra = "The provided access token was invalid."
                elif user.is_anonymous:
                    perms = Permission.NONUSER
                elif user.is_admin:
                    perms = Permission.ADMIN
                elif not user.is_active():
                    perms = Permission.NONUSER
                    extra = "User is not active."
                else:
                    perms = Permission.USER

            if perms < min_level:
                title = "Insufficient permissions to access this resource"
                raise JsonApiException(
                    title=title,
                    detail=extra,
                    status=403,
                )

            kwargs["user"] = user
            kwargs["permission"] = perms
            return function(*args, **kwargs)

        return user_wrap_function

    return wrapper
