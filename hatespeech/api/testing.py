from hatespeech.api.database import db
from hatespeech.api.app import app
from hatespeech.api.logging2 import log
from flask import Blueprint, Response, jsonify, request

mod = Blueprint('testing', __name__)

_TEST_DATA = [
    {'word': 'existingword'},
    {'word': 'hate'},
]


@app.route('/testing/setup')
def setup():
    try:
        db.hateword.delete_many({})
        db.hateword.insert(_TEST_DATA)
        return ''
    except Exception as e:
        return Response(e, status=400)


@app.route('/testing/teardown')
def teardown():
    try:
        db.hateword.delete_many({})
        return ''
    except Exception as e:
        return Response(e, status=400)