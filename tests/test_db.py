import unittest
import flask_pymongo
from unittest import mock


class DatabaseTestCase(unittest.TestCase):

    @mock.patch("flask_pymongo.PyMongo")
    def test_connection(self, mock_mongoclient):
        from api import database
        db = database.mongo.db
        print(db)
        assert db is not None