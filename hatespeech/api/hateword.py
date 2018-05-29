from hatespeech.api.database import db
from hatespeech.api.app import app
from hatespeech.api.logging2 import log
from flask import Blueprint, Response, jsonify, request


mod = Blueprint('hateword', __name__)


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
    try:
        req = request.get_json(force=True)
        if not req:
            return Response("Supplied data format is malformed", status=401)

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
            return ""
        elif result.upserted_id is not None:
            log.info(f"Added new hate word [{req['word']}]: {obj}")
            return ""
        else:
            raise RuntimeError("Unknown error")
    except Exception as e:
        return Response(e, status=401)


@app.route('/hatewords', methods=['DELETE'])
def _delete_hate_word():
    """Delete a hate word from the list."""
    try:
        req = request.get_json(force=True)
        if not req:
            return Response("Supplied data format is malformed", status=401)

        result = db.hateword.delete_one({
            'word': req['word']
        })

        if result.deleted_count == 1:
            log.info(f"Deleted hate word [{req['word']}]")
            return ""
        else:
            return Response(f"Unable to delete hate word [{req['word']}]", 401)
    except Exception as e:
        return Response(e, status=401)


# ============================================================================
# Interface for other Python modules

def get_hate_word_list():
    """Retrieve the list of hate words."""
    return list(i['word'] for i in db.hateword.find())