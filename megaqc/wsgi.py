import os
from megaqc.app import create_app
from megaqc.settings import TestConfig, DevConfig, ProdConfig


if os.environ.get('MEGAQC_DEBUG', False):
    CONFIG = DevConfig()
elif os.environ.get('MEGAQC_PRODUCTION', False):
    CONFIG = ProdConfig()
else:
    CONFIG = TestConfig()

app = create_app(CONFIG)
