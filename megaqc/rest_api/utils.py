import os
from flask.globals import current_app
from uuid import uuid4


def get_upload_dir():
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    return upload_dir


def get_unique_filename():
    dir = get_upload_dir()
    while True:
        proposed = os.path.join(dir, str(uuid4()))
        if not os.path.exists(proposed):
            return proposed
