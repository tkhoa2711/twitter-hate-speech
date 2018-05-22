import json
import unittest
from hatespeech.api.database import db


class HateSpeechTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            from hatespeech.api.app import app
            cls.app = app.test_client()
        except Exception as e:
            raise unittest.SkipTest(e)

    def setUp(self):
        try:
            # clear existing data and insert test data
            db.hateword.delete_many({})
            db.hateword.insert([
                {'word': 'test'},
                {'word': 'hate'},
            ])
        except Exception as e:
            raise unittest.SkipTest(e)

    def tearDown(self):
        # clear test data
        db.hateword.delete_many({})

    def test_get_new_hateword(self):
        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        assert data[0]['word'] == 'test'
        assert data[1]['word'] == 'hate'

    def test_add_new_hateword(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'speech'}),
                            content_type='application/json')

        assert res.status_code == 200

    def test_update_hateword(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'test', 'category': 'opinion'}),
                            content_type='application/json')

        assert res.status_code == 200

    def test_delete_hateword(self):
        res = self.app.delete('/hatewords',
                              data=json.dumps({'word': 'test'}),
                              content_type='application/json')

        assert res.status_code == 200
