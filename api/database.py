from flask_pymongo import PyMongo
from api.app import app

# The MongoDB instance
# NOTE: we can't directly use db = mongo.db due to Flask's application context
mongo = PyMongo(app)