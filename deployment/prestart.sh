#! /usr/bin/env bash

# Let the DB start
sleep 10

# Create the DB, ignoring errors, such as if the database already exists
megaqc initdb || true

# Run migrations
cd megaqc
export FLASK_APP=wsgi.py
flask db upgrade
