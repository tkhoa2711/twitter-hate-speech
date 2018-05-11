from api.database import db
from api.app import app
from flask import Blueprint, jsonify, request


mod = Blueprint('hatespeech', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation

@app.route('/hatewords')
def _get_hate_word_list():
    """Retrieve the list of hate words."""
    import json
    from bson import json_util
    result = db.hateword.find()
    return jsonify(result=[
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in result
    ])


@app.route('/hatewords', methods=['POST'])
def _set_hate_word():
    """Add a new hate word to the list or update existing one."""
    req = request.get_json()
    db.hateword.replace_one({
        'word': req['word']
    },
    {
        'word': req['word'],
        'category': req.get('category'),
        'similar_to': req.get('similar_to'),
    },
    upsert=True)


@app.route('/hatewords', methods=['DELETE'])
def _delete_hate_word():
    """Delete a hate word from the list."""
    req = request.get_json()
    db.hateword.delete_one({
        'word': req['word']
    })


# ============================================================================
# Interface for other Python modules

def get_hate_word_list():
    """Retrieve the list of hate words."""
    return list(i['word'] for i in db.hateword.find())