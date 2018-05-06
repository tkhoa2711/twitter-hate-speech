from flask import Flask
from flask_cors import CORS
from config import config
import os

app = Flask(__name__)

CORS(app, supports_credentials=True)
env = os.environ.get('FLASK_ENV', 'dev')
app.config.from_object(config)
