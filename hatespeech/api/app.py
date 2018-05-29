import http
import os
from flask import Flask
from flask_cors import CORS
from hatespeech.config import config


app = Flask(__name__)

# enable support for CORS
CORS(app, supports_credentials=True)

# configure environment variables
env = os.environ.get('FLASK_ENV', 'dev')
app.config.from_object(config)

# set secret key for session management
app.secret_key = os.urandom(16)


# ============================================================================

@app.route('/app/start')
def start():
    """
    API for starting/resuming the Twitter streaming.
    """
    app.twitter_stream.start()
    return '', http.HTTPStatus.NO_CONTENT


@app.route('/app/stop')
def stop():
    """
    API for stopping streaming from Twitter.
    """
    app.twitter_stream.stop()
    return '', http.HTTPStatus.NO_CONTENT
