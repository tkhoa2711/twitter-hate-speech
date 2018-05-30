# -*- coding: utf-8 -*-
import threading
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


# ============================================================================
# Helper functions for performing safe operations on a dictionary object

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


# ============================================================================
# Threading helper functions

class StoppableThread(threading.Thread):
    """
    A class for thread that is stoppable.
    This class aims at functions that need to run in an infinite loop and sleep in between.
    Use the provided helper methods to implement this stoppable feature.

    NOTE: Instances of this class should be started with :func:`start_thread`
    in order to be able to stopped collectively with :func:`stop_all_threads`.
    """

    def __init__(self):
        super(StoppableThread, self).__init__()
        self.__stop = threading.Event()
        self.__cond = threading.Condition()

    def stop(self):
        """
        Stop the thread.
        """
        self.__stop.set()
        with self.__cond:
            self.__cond.notify_all()

    def is_stopped(self):
        """
        Check whether the thread is already stopped.

        :return:    True if already stopped, False otherwise
        """
        return self.__stop.is_set()

    def sleep(self, interval):
        """
        Sleep for a given interval or until being stopped intentionally.

        :param interval:    the sleeping interval in seconds
        """
        with self.__cond:
            self.__cond.wait(timeout=interval)


"""
This list holds all the stoppable threads.
"""
__threads = []


def start_thread(t):
    """
    Start a thread implementing :class:`StoppableThread`.

    :param t:   the thread instance to start
    """
    global __threads
    __threads.append(t)
    t.start()


def stop_all_threads():
    """
    Stop all threads that were started with :func:`start_thread`.
    """
    global __threads
    for t in __threads:
        t.stop()
