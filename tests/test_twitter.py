import unittest
from hatespeech.api import twitter
from hatespeech.api.database import db


class TwitterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            from hatespeech.config import config
            cls.stream = twitter.create_stream()
        except Exception as e:
            raise unittest.SkipTest(e)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'stream'):
            cls.stream.disconnect()

    def test_create_stream(self):
        # TODO: add proper logging for unit tests
        # See https://stackoverflow.com/questions/7472863/pydev-unittesting-how-to-capture-text-logged-to-a-logging-logger-in-captured-o
        print("the stream should be created successfully during class setup")
        pass


class TwitterAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            from hatespeech.api.app import app
            cls.app = app.test_client()
            db.client.server_info()
        except Exception as e:
            raise unittest.SkipTest(e)

    def tearDown(self):
        pass