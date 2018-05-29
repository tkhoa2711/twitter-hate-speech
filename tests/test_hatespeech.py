import json
import unittest
from hatespeech.api.database import db


class HateWordTest(unittest.TestCase):

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
            db.hateword.insert_many([
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

    def test_add_new_hateword_normalized(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'SpEech'}),
                            content_type='application/json')

        assert res.status_code == 200

        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        assert data[2]['word'] == 'speech'

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


class HateWordCategoryTest(unittest.TestCase):

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
            db.hateword.insert_many([
                {'word': 'test', 'category': [], 'similar_to': ['test']},
                {'word': 'hate', 'category': ['personal'], 'similar_to': []},
            ])

            db.category.delete_many({})
            db.category.insert_many([
                {'name': 'personal'},
            ])
        except Exception as e:
            raise unittest.SkipTest(e)

    def tearDown(self):
        # clear test data
        db.hateword.delete_many({})
        db.category.delete_many({})

    def test_add_hateword_with_empty_category(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'speech', 'category': []}),
                            content_type='application/json')

        assert res.status_code == 200

        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        obj = data[2]
        assert obj['word'] == 'speech'
        assert obj['category'] == []

    def test_add_hateword_with_category(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'speech', 'category': ['cate1', 'cate2']}),
                            content_type='application/json')

        assert res.status_code == 200

        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        obj = data[2]
        assert obj['word'] == 'speech'
        assert obj['category'] == ['cate1', 'cate2']

        # check database
        res = list(db.category.find())
        assert res[0]['name'] == 'personal'
        assert res[1]['name'] == 'cate1'
        assert res[2]['name'] == 'cate2'

    def test_add_hateword_with_category_normalized(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'speech', 'category': ['Cate1', 'Cate 2']}),
                            content_type='application/json')

        assert res.status_code == 200

        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        obj = data[2]
        assert obj['word'] == 'speech'
        assert obj['category'] == ['cate1', 'cate 2']

        # check database
        res = list(db.category.find())
        assert res[0]['name'] == 'personal'
        assert res[1]['name'] == 'cate1'
        assert res[2]['name'] == 'cate 2'

    def test_update_category(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'hate', 'category': ['cate1']}),
                            content_type='application/json')

        assert res.status_code == 200

        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        obj = data[1]
        assert obj['word'] == 'hate'
        assert obj['category'] == ['cate1']

        # check database
        res = list(db.category.find())
        assert res[0]['name'] == 'personal'
        assert res[1]['name'] == 'cate1'

    def test_update_category2(self):
        res = self.app.post('/hatewords',
                            data=json.dumps({'word': 'hate', 'category': ['personal', 'cate1']}),
                            content_type='application/json')

        assert res.status_code == 200

        res = self.app.get('/hatewords')
        data = json.loads(res.data)['result']

        assert type(data) == list
        obj = data[1]
        assert obj['word'] == 'hate'
        assert obj['category'] == ['personal', 'cate1']

        # check database
        res = list(db.category.find())
        assert res[0]['name'] == 'personal'
        assert res[1]['name'] == 'cate1'
