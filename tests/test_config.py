# -*- coding: utf-8 -*-
"""
Test configs.
"""
import pytest

from megaqc.app import create_app
from megaqc.settings import DevConfig, ProdConfig


@pytest.mark.noautofixt
def test_production_config():
    """
    Production config.
    """
    app = create_app(ProdConfig)
    assert app.config["ENV"] == "prod"
    assert app.config["DEBUG"] is False
    assert app.config["DEBUG_TB_ENABLED"] is False


@pytest.mark.noautofixt
def test_dev_config():
    """
    Development config.
    """
    app = create_app(DevConfig)
    assert app.config["ENV"] == "dev"
    assert app.config["DEBUG"] is True
