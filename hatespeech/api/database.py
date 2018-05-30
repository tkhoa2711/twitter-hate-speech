import http
import logging
from datetime import datetime
from flask_pymongo import PyMongo
from hatespeech.api.app import app
from hatespeech.api.logging2 import log

try:
    mongo = PyMongo(app)
    db = None
    with app.app_context():
        db = mongo.db
except Exception as e:
    log = logging.getLogger(__name__)
    log.exception(e)


@app.route('/db/recreate')
def recreate_db():
    """
    Recreate the database.
    """
    import pymongo
    from script import script

    # table for storing categories of hate words
    db.category.drop()
    db.category.create_index([('name', pymongo.ASCENDING)], unique=True)

    # table for storing hate words
    db.hateword.drop()
    db.hateword.create_index([('word', pymongo.ASCENDING)], unique=True)
    script.populate_hateword_data()

    # table for storing tweets
    db.tweet.drop()

    # table for storing processed tweets
    db.result.drop()
    db.result.create_index([('id', pymongo.ASCENDING)], unique=True)

    # table for storing user info
    db.user.drop()
    db.user.create_index([('username', pymongo.ASCENDING)], unique=True)
    script.populate_user_data()

    log.info("Recreated database successfully")
    return '', http.HTTPStatus.NO_CONTENT


@app.route('/db/clean')
def clean_old_data(days=7):
    """
    Clean tweet data that is older than 7 days (by default).
    """
    now = int(datetime.now().timestamp() * 1000)
    date_range = days * 86400 * 1000
    date_threshold = now - date_range

    result = db.result.delete_many({'timestamp_ms': {'$lt': date_threshold}})

    log.info(f"Deleted {result.deleted_count} tweet records")
    return '', http.HTTPStatus.NO_CONTENT