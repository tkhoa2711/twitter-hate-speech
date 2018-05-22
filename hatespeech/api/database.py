import logging
from flask_pymongo import PyMongo
from hatespeech.api.app import app

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

    # table for storing hate words
    db.hateword.drop()
    db.hateword.create_index([('word', pymongo.ASCENDING)], unique=True)
    script.populate_hateword_data()

    # table for storing tweets
    db.tweet.drop()

    # table for storing processed tweets
    db.result.drop()

    import http
    return '', http.HTTPStatus.NO_CONTENT
