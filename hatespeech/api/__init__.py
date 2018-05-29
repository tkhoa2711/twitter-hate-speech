from hatespeech.api.app import app

# import and register blueprints
from hatespeech.api import auth
app.register_blueprint(auth.mod)

from hatespeech.api import twitter
app.register_blueprint(twitter.mod)

from hatespeech.api import hateword
app.register_blueprint(hateword.mod)

from hatespeech.api import testing
app.register_blueprint(testing.mod)
