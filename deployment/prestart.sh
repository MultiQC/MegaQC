#! /usr/bin/env bash

# Let the DB start
sleep 10

# Create the DB
megaqc initdb

# Run migrations
cd megaqc
export FLASK_APP=wsgi.py
