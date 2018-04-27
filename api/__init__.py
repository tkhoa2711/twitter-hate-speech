from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from config import config
import os

app = Flask(__name__)
mongo = PyMongo(app)

CORS(app)
env = os.environ.get('FLASK_ENV', 'dev')
app.config.from_object(config)

# import and register blueprints
from api.views import main
app.register_blueprint(main.mod)

from api import twitter
app.register_blueprint(twitter.mod)
