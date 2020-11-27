import os

from environs import Env

from megaqc.app import create_app
from megaqc.settings import DevConfig, ProdConfig, TestConfig

env = Env()
env.read_env()

if env.bool("FLASK_DEBUG", False):
    CONFIG = DevConfig()
elif env.bool("MEGAQC_PRODUCTION", False):
    CONFIG = ProdConfig()
else:
    CONFIG = TestConfig()

app = create_app(CONFIG)
