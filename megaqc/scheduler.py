# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import gzip
import io
import json
import os
import traceback
from builtins import str

from flask import current_app
from flask_apscheduler import APScheduler
from megaqc.api.utils import handle_report_data
from megaqc.extensions import db
from megaqc.model.models import Upload
from megaqc.user.models import User

scheduler = APScheduler()


def init_scheduler(app):
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()


def upload_reports_job():
    with scheduler.app.app_context():
        queued_uploads = (
            db.session.query(Upload).filter(Upload.status == "NOT TREATED").all()
        )
        for row in queued_uploads:
            user = db.session.query(User).filter(User.user_id == row.user_id).one()
            current_app.logger.info(
                "Beginning process of upload #{} from {}".format(
                    row.upload_id, user.email
                )
            )
            row.status = "IN TREATMENT"
            db.session.add(row)
            db.session.commit()
            # Check if we have a gzipped file
            gzipped = False
            with open(row.path, "rb") as fh:
                # Check if we have a gzipped file
                file_start = fh.read(3)
                if file_start == b"\x1f\x8b\x08":
                    gzipped = True
            try:
                if gzipped:
                    with io.BufferedReader(gzip.open(row.path, "rb")) as fh:
                        raw_data = fh.read().decode("utf-8")
                else:
                    with io.open(row.path, "rb") as fh:
                        raw_data = fh.read().decode("utf-8")
                data = json.loads(raw_data)
                # Now save the parsed JSON data to the database
                ret = handle_report_data(user, data)
            except Exception:
                ret = (
                    False,
                    "<pre><code>{}</code></pre>".format(traceback.format_exc()),
                )
                current_app.logger.error(
                    "Error processing upload {}: {}".format(
                        row.upload_id, traceback.format_exc()
                    )
                )
            if ret[0]:
                row.status = "TREATED"
                row.message = "The document has been uploaded successfully"
                os.remove(row.path)
            else:
                if ret[1] == "Report already processed":
                    current_app.logger.info(
                        "Upload {} already being processed by another worker, skipping".format(
                            row.upload_id
                        )
                    )
                    continue
                row.status = "FAILED"
                row.message = "The document has not been uploaded : {0}".format(ret[1])
            row.modified_at = datetime.datetime.utcnow()
            current_app.logger.info(
                "Finished processing upload #{} to state {}".format(
                    row.upload_id, row.status
                )
            )
            db.session.add(row)
            db.session.commit()
