import logging
from flask_pymongo import PyMongo
from api.app import app

try:
    mongo = PyMongo(app)
    db = None
    with app.app_context():
        db = mongo.db
except Exception as e:
    log = logging.getLogger(__name__)
    log.exception(e)