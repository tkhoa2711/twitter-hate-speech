import unittest
from api import hatespeech
from api.database import mongo


class HateSpeechTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            mongo.db.hateword.insert([
                {'word': 'test'},
                {'word': 'hate'},
            ])
        except Exception as e:
            raise unittest.SkipTest(e)

    @classmethod
    def tearDownClass(cls):
        mongo.db.hateword.remove({})

    def test_get_hate_word_list(self):
        # assert hatespeech.get_hate_word_list() == ['test', 'hate']
        pass
