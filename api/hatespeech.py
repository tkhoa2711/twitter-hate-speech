from api.database import db
from api.app import app
from flask import Blueprint, jsonify


mod = Blueprint('hatespeech', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation

@app.route('/hatewords')
def get_hate_word_list():
    """Retrieve the list of hate words."""
    import json
    from bson import json_util
    result = db.hateword.find()
    return jsonify(result=[
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in result
    ])


@app.route('/hatewords', methods=['POST'])
def set_hate_word_list(lst):
    """Set the hate word list."""
    # TODO: implementation
    pass
