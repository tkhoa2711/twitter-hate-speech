import unittest


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        # create a test client of the app
        import hatespeech.api
        self.app = hatespeech.api.app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_index(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 404)