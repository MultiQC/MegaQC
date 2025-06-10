# -*- coding: utf-8 -*-
"""
Main application package.
"""
try:
    from importlib.metadata import version as get_version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import version as get_version

version = get_version("megaqc")
