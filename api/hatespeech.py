from api.database import mongo
from api.app import app
from flask import Blueprint, jsonify


mod = Blueprint('hatespeech', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation

@app.route('/hatewords')
def get_hate_word_list():
    """Retrieve the list of hate words."""
    return jsonify(result=list(i['word'] for i in mongo.db.hateword.find()))


@app.route('/hatewords', methods=['POST'])
def set_hate_word_list(lst):
    """Set the hate word list."""
    # TODO: implementation
    mongo.db.hateword.insert(lst)
