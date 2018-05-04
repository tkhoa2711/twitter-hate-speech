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
    stream.start()
    app.run(debug=True, host='0.0.0.0', port=5000)
    stream.stop()


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


if __name__ == '__main__':
    manager.run()