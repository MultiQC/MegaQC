# -*- coding: utf-8 -*-
"""Application assets."""
from flask_assets import Bundle, Environment

# ///////
# ASSETS ONLY USED IN DEBUG MODE
# In production, combined + minified grunt versions are used

css = Bundle(
    'libs/font-awesome/css/font-awesome.min.css',
    'scss/main.css'
)

js = Bundle(
    'libs/jquery/dist/jquery.min.js',
    'libs/tether/dist/js/tether.min.js',
    'libs/bootstrap/dist/js/bootstrap.min.js',
    'js/plugins.js',
    output='public/js/common.js'
)

assets = Environment()

assets.register('js_all', js)
assets.register('css_all', css)
