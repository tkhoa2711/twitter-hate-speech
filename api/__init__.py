from flask import Flask
from flask_cors import CORS
from config.config import config
import os


app = Flask(__name__)

CORS(app)
env = os.environ.get('FLASK_ENV', 'dev')
app.config.from_object(config[env])

# import and register blueprints
from api.views import main
app.register_blueprint(main.mod)
