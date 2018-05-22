# -*- coding: utf-8 -*-
from flask import jsonify


def create_response(data={}, status=200, message=''):
    """
    Wraps response in a consistent format throughout the API
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response

    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself
    """
    if type(data) is not dict:
        raise TypeError('Data should be a dictionary 😞')
        
    response = {
        'success': 200 <= status < 300,
        'code': status,
        'message': message,
        'result': data
    }
    return jsonify(response), status


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def safe_get(lst, index, default=None):
    """
    An implementation of the similar :meth:`get` of the dictionary class.
    :param lst:     the list to perform the operation on
    :param index:   the index to query
    :param default: the default value if not found
    :return:        the result if exists or the default value
    """
    try:
        return lst[index]
    except IndexError:
        return default


def safe_get_dict(dct, keys, default=None, ignore_none=True):
    """
    A utility function to extract value from nested dictionary.

    :param dct:         the top-level dictionary object
    :param keys:        the list of keys to extract from
    :param default:     the default value if nothing is found
    :param ignore_none: None value is considered as non existing, default is True
                        When set to False, if a None is faced in the middle of extracting process,
                        a TypeError exception will be raised.
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            dct = default
        except TypeError:
            if ignore_none:
                dct = default
            else:
                raise
    return dct
