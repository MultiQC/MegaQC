import os
from megaqc.app import create_app
from megaqc.settings import TestConfig, DevConfig, ProdConfig
CONFIG = TestConfig()
if os.environ.get('MEGAQC_DEBUG', False):
    CONFIG = DevConfig()
elif os.environ.get('MEGAQC_PRODUCTION', False):
    CONFIG = ProdConfig()
create_app(CONFIG)
