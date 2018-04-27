from api import app
from flask import Blueprint
from api.utils import create_response

mod = Blueprint('main', __name__)

# function that is called when you visit /
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

# function that is called when you visit /persons
@app.route('/persons')
def name():
    try:
        pass
        # create_response(data=Person.query.all())
    except Exception as ex:
        return create_response(data={}, status=400, message=str(ex))