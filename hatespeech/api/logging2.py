import logging
from flask import logging as flask_logging
from hatespeech.api.app import app
from hatespeech.config import config

flask_logging.DEBUG_LOG_FORMAT = (
    '[%(asctime)s] %(levelname)s %(filename)s.%(funcName)s [%(pathname)s:%(lineno)d] [%(thread)d]:\n' +
    '%(message)s\n' +
    '-' * 80
)

file_handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(flask_logging.DEBUG_LOG_FORMAT))
app.logger.addHandler(file_handler)

log = app.logger
