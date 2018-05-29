import unittest
from hatespeech.api.database import db


class DatabaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            from hatespeech.api.app import app
            cls.app = app.test_client()
            db.client.server_info()
        except Exception as e:
            raise unittest.SkipTest(e)
