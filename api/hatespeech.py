from api.database import db
from api.app import app
from api.logging import log
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
    obj = {
        'word': req['word'],
        'category': req.get('category'),
        'similar_to': req.get('similar_to'),
    }
    result = db.hateword.replace_one({
        'word': req['word']
    }, obj, upsert=True)

    if result.modified_count == 1:
        log.info(f"Updated hate word [{req['word']}]: {obj}")
    elif result.upserted_id is not None:
        log.info(f"Added new hate word [{req['word']}]: {obj}")


@app.route('/hatewords', methods=['DELETE'])
def _delete_hate_word():
    """Delete a hate word from the list."""
    req = request.get_json()
    result = db.hateword.delete_one({
        'word': req['word']
    })

    if result.deleted_count == 1:
        log.info(f"Deleted hate word [{req['word']}]")


# ============================================================================
# Interface for other Python modules

def get_hate_word_list():
    """Retrieve the list of hate words."""
    return list(i['word'] for i in db.hateword.find())