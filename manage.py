from config import config # NOTE: call this first to properly initialize all configs
from api import app
from api import twitter
from flask_script import Manager


manager = Manager(app)


@manager.command
def dev():
    """
    Run the server in development mode.
    """
    stream = twitter.create_stream(config)
    app.twitter_stream = stream
    app.twitter_stream.start()
    app.run(debug=True, host='0.0.0.0', port=config.PORT, use_reloader=False, threaded=True)
    app.twitter_stream.stop()


@manager.command
def prod():
    """
    Run the server in production mode.
    """
    app.run(debug=False)


@manager.command
def test():
    """
    Run all the tests.
    """
    import unittest

    # TODO: refactor this part, have a proper environment for QA/testing
    import os
    os.environ['FLASK_ENV'] = 'dev'

    tests = unittest.TestLoader().discover('tests', pattern="*test*.py")
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreate the database.
    """
    import pymongo
    from api.database import db
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


if __name__ == '__main__':
    manager.run()
