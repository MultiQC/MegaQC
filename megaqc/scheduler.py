
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from megaqc.model.models import Upload
from megaqc.user.models import User
from megaqc.extensions import db
from megaqc.api.utils import handle_report_data
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

import json
import datetime

def start_job_scheduler(url):
    import logging
    logging.basicConfig()
    scheduler = BackgroundScheduler()
    scheduler.add_job(upload_reports_job, args=[url], trigger='interval', seconds=30)
    scheduler.start()

def upload_reports_job(url):
    engine = create_engine(url)
    Session = sessionmaker()
    session = Session(bind=engine)
    queued_uploads = session.query(Upload).filter(Upload.status == "NOT TREATED").all()
    for row in queued_uploads:
        row.status = "IN TREATMENT"
        row.save()
        user = session.query(User).filter(User.user_id == row.user_id).one()
        data = json.load(row.path)
        try:
            ret = handle_report_data(user, data)
        except Exception as e:
            ret=(False, e.strerror)
        if ret[0]:
            row.status = "TREATED"
            row.message = "The document has been uploaded successfully"
        else:
            row.status = "FAILED"
            row.message = "The document has not been uploaded : {0}".format(ret[1])
        row.modified_at = datetime.datetime.utcnow()
        row.save()



