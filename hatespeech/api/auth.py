from functools import wraps
from flask import request, session, Blueprint, Response
from hatespeech.api.app import app
from hatespeech.api.database import db
from hatespeech.api.logging2 import log


mod = Blueprint('auth', __name__)


@app.route('/auth/login', methods=['POST'])
def login():
    if not session.get('username'):
        req = request.get_json(force=True)
        username = req.get('username')
        password = req.get('password')

        if not username or not password:
            return Response('Input format is invalid', status=400)

        user = db.user.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            log.info(f"User [{username}] has just logged in")
            return 'Successful'
        else:
            return Response('Username or password is incorrect', status=401)
    else:
        return 'User already logged in'


@app.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    log.info(f"User [{username}] has just logged out")
    return 'Logged out'


def authorize(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return Response('Access denied', status=401)

        return func(*args, **kwargs)
    return wrapper
