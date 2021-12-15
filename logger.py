import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler


FORMATTER = logging.Formatter(
    "%(asctime)s:%(name)s:%(module)s:%(levelname)s:%(message)s"
    )
LOG_FILE = os.environ["MEGAQC_FULL_LOG"]


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when='W0', backupCount=1
    )
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())

    logger.propagate = False
    return logger
