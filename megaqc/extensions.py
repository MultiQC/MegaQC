# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
