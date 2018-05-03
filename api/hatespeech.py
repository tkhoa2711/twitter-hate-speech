from api.database import mongo
from api.app import app
from flask import Blueprint


mod = Blueprint('hatespeech', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation

@app.route('/hatewords')
def get_hate_word_list():
    """Retrieve the list of hate words."""
    return list(i['word'] for i in mongo.db.hateword.find())


@app.route('/hatewords', methods=['POST'])
def set_hate_word_list(lst):
    """Set the hate word list."""
    # TODO: implementation
    return mongo.db.hateword.insert(lst)
