import unittest
from api import twitter


class TwitterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from config import config
        cls.stream = twitter.create_stream(config)

    @classmethod
    def tearDownClass(cls):
        cls.stream.disconnect()

    def test_create_stream(self):
        # TODO: add proper logging for unit tests
        # See https://stackoverflow.com/questions/7472863/pydev-unittesting-how-to-capture-text-logged-to-a-logging-logger-in-captured-o
        print("the stream should be created successfully during class setup")
        pass