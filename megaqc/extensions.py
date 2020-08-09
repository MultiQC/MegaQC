# -*- coding: utf-8 -*-
"""
Extensions module.

Each extension is initialized in the app factory located in app.py.
"""
from pathlib import Path

from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_rest_jsonapi import Api as JsonApi
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
ma = Marshmallow()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
restful = Api(prefix="/rest_api/v1")
migrate = Migrate(directory=str(Path(__file__).parent / "migrations"))
json_api = JsonApi()
