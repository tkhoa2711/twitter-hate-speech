from hatespeech.config import config # NOTE: call this first to properly initialize all configs
from hatespeech.api import (
    app,
    sentiment,
    twitter,
)
from hatespeech.api.logging2 import log
from flask_script import Manager


# ============================================================================
# Essential app initialization here

def init_app():
    sentiment.init()

    stream = twitter.create_stream()
    app.twitter_stream = stream
    app.twitter_stream.start()

    # start monitoring disk space only if mongodb is running in the same host
    if any(i in config.MONGO_URI for i in ('localhost', '127.0.0.1')):
        from hatespeech.disk_space_monitor import monitor_disk_usage
        monitor_disk_usage()


def teardown_app():
    if app.twitter_stream:
        app.twitter_stream.stop()

    # stop all dependent threads
    from hatespeech.api.utils import stop_all_threads
    stop_all_threads()


# ============================================================================
# Commands for executing the managing script

manager = Manager(app)


@manager.command
def dev():
    """
    Run the server in development mode.
    """
    init_app()
    app.run(debug=True, host='0.0.0.0', port=config.PORT, use_reloader=False, threaded=True)


@manager.command
def prod():
    """
    Run the server in production mode.
    """
    init_app()
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
    from hatespeech.api.database import recreate_db
    recreate_db()


@manager.command
def train_model():
    """
    Train the Naive Bayes classifier model for sentiment analysis.
    """
    from hatespeech.api.sentiment import train_and_test_classifier
    train_and_test_classifier()


@manager.command
def gunicorn():
    """
    Start the Server with Gunicorn.
    """
    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {}

        def load(self):
            init_app()
            return app

    application = FlaskApplication()
    return application.run()


if __name__ == '__main__':
    try:
        manager.run()
    except (KeyboardInterrupt, SystemExit):
        log.info("Stopping the app")
        teardown_app()
