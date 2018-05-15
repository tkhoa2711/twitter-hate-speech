from api.app import app

# import and register blueprints
from api.views import main
app.register_blueprint(main.mod)

from api import twitter
app.register_blueprint(twitter.mod)

from api import hatespeech
app.register_blueprint(hatespeech.mod)

from api import testing
app.register_blueprint(testing.mod)
