from hatespeech.api.app import app

# import and register blueprints
from hatespeech.api import twitter
app.register_blueprint(twitter.mod)

from hatespeech.api import hatespeech
app.register_blueprint(hatespeech.mod)

from hatespeech.api import testing
app.register_blueprint(testing.mod)
