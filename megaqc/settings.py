# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from megaqc.scheduler import upload_reports_job
import yaml


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('MEGAQC_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JOBS = [{'id': 'job1','func': upload_reports_job,'trigger': 'interval','seconds': 30}]
    SCHEDULER_API_ENABLED = True
    EXTRA_CONFIG = os.environ.get("MEGAQC_CONFIG", None)
    SERVER_NAME = None

    def __init__(self):
        if self.EXTRA_CONFIG:
            with open(self.EXTRA_CONFIG) as f:
                self.extra_conf = yaml.load(f)
                for key in self.extra_conf:
                    if key in self.__dict__:
                        setattr(self, self.extra_conf[key])
                        print("Setting {} to {}".format(key, self.extra_conf[key]))
                    else:
                        print("Key '{}' not in '{}'".format(key, self.__dict__))
            if self.SQLALCHEMY_DBMS == "sqlite":
                self.SQLALCHEMY_DATABASE_URI = '{0}://{1}'.format(self.SQLALCHEMY_DBMS, self.DB_PATH)
            else:
                self.SQLALCHEMY_DATABASE_URI = '{3}://{0}:@{1}/{2}'.format(self.SQLALCHEMY_USER, self.SQLALCHEMY_HOST, self.SQLALCHEMY_DATABASE, self.SQLALCHEMY_DBMS)


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DBMS = 'postgresql'
    SQLALCHEMY_USER = 'megaqc_user'
    SQLALCHEMY_HOST='localhost:5432'
    SQLALCHEMY_DATABASE = 'megaqc'
    SQLALCHEMY_DATABASE_URI = '{3}://{0}:@{1}/{2}'.format(SQLALCHEMY_USER, SQLALCHEMY_HOST, SQLALCHEMY_DATABASE, SQLALCHEMY_DBMS)
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar

    def __init__(self):
        super(ProdConfig, self).__init__()
        # Log to the terminal
        print(" * Database type: {}".format(self.SQLALCHEMY_DBMS))
        print(" * Database path: {}".format(self.SQLALCHEMY_DATABASE_URI))


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DBMS = 'sqlite'
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = '{0}:///{1}'.format(SQLALCHEMY_DBMS,DB_PATH)
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    WTF_CSRF_ENABLED = False  # Allows form testing

    def __init__(self):
        super(DevConfig, self).__init__()
        # Log to the terminal
        print(" * Database type: {}".format(self.SQLALCHEMY_DBMS))
        print(" * Database path: {}".format(self.DB_PATH))



class TestConfig(Config):
    """Test configuration."""
    SQLALCHEMY_DBMS = 'sqlite'
    DB_NAME = 'test.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = '{0}:///{1}'.format(SQLALCHEMY_DBMS,DB_PATH)

    def __init__(self):
        super(TestConfig, self).__init__()
