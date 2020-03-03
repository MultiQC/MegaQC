import os
from enum import IntEnum, auto
from functools import wraps
from uuid import uuid4

from flask import request
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
    VIEWER = auto()
    USER = auto()
    ADMIN = auto()


def check_perms(function):
    """
    Adds a "user" and "permission" kwarg to the view function.

    :param function:
    :return:
    """

    @wraps(function)
    def user_wrap_function(*args, **kwargs):
        if not request.headers.has_key("access_token"):
            perms = Permission.VIEWER
            user = None
        else:
            user = User.query.filter_by(
                api_token=request.headers.get("access_token")
            ).first()
            if not user:
                perms = Permission.VIEWER
            elif user.is_anonymous:
                perms = Permission.VIEWER
            elif user.is_admin:
                perms = Permission.ADMIN
            else:
                perms = Permission.USER

        kwargs["user"] = user
        kwargs["permission"] = perms
        return function(*args, **kwargs)

    return user_wrap_function
