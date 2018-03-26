from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from config.config import config
import os

app = Flask(__name__)
mongo = PyMongo(app)

CORS(app)
env = os.environ.get('FLASK_ENV', 'dev')
app.config.from_object(config[env])

# import and register blueprints
from api.views import main
app.register_blueprint(main.mod)
