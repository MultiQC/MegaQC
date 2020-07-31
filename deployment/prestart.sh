#! /usr/bin/env bash

# Let the DB start
sleep 10

# Create the DB
megaqc initdb

# Run migrations
export FLASK_APP=megaqc/wsgi.py
flask db upgrade
