from hatespeech.api.database import db
from hatespeech.api.app import app
from hatespeech.api.auth import authorize
from hatespeech.api.logging2 import log
from flask import Blueprint, Response, jsonify, request


mod = Blueprint('hateword', __name__)


# ============================================================================
# API for managing and using tweet data

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
@authorize
def _set_hate_word():
    """Add a new hate word to the list or update existing one."""
    try:
        req = request.get_json(force=True)
        if not req:
            return Response("Supplied data format is malformed", status=400)

        hateword = _normalize(req['word'])
        categories = [_normalize(i) for i in req.get('category', [])]
        similar_words = [_normalize(i) for i in req.get('similar_to', [])]

        obj = {
            'word': hateword,
            'category': categories,
            'similar_to': similar_words,
        }

        # add/update the word in db
        result = db.hateword.replace_one({
            'word': hateword
        }, obj, upsert=True)

        # add new categories if there are any
        for cate in categories:
            db.category.update_one({
                'name': cate
            }, {
                '$setOnInsert': {'name': cate}
            }, upsert=True)

        # check result
        if result.modified_count == 1:
            log.info(f"Updated hate word [{hateword}]: {obj}")
            return ""
        elif result.upserted_id is not None:
            log.info(f"Added new hate word [{hateword}]: {obj}")
            return ""
        else:
            raise RuntimeError("Unknown error")
    except Exception as e:
        return Response(e, status=500)


@app.route('/hatewords', methods=['DELETE'])
@authorize
def _delete_hate_word():
    """Delete a hate word from the list."""
    try:
        req = request.get_json(force=True)
        if not req:
            return Response("Supplied data format is malformed", status=400)

        result = db.hateword.delete_one({
            'word': req['word']
        })

        if result.deleted_count == 1:
            log.info(f"Deleted hate word [{req['word']}]")
            return ""
        else:
            return Response(f"Unable to delete hate word [{req['word']}]", 400)
    except Exception as e:
        return Response(e, status=500)


# ============================================================================
# Interface for other Python modules

def get_hate_word_list():
    """Retrieve the list of hate words."""
    return list(i['word'] for i in db.hateword.find())


def _normalize(word):
    word = word.lower()
    return word