import dill as pickle
import redis
from abc import ABC, abstractmethod


class MessageQueue(ABC):

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def push(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def pop(self, *args, **kwargs):
        pass


class RedisQueue(MessageQueue):

    def __init__(self, url, *args, **kwargs):
        self._queue = redis.from_url(url)
        self._key = kwargs.pop('key', '')

    def push(self, msg, key=''):
        key = self._key if not key else key
        return self._queue.rpush(key, pickle.dumps(msg))

    def pop(self, key=''):
        key = self._key if not key else key
        return pickle.loads(self._queue.blpop(key)[1])


def connect_to_message_queue(*args, **kwargs):
    """
    Create a connection to a message queue according to the application config.
    :return:    the corresponding queue connection object
    """
    from hatespeech.api.logging2 import log
    from hatespeech.config import config

    log.info(f"Connecting to queue with config: args {args}, kwargs {kwargs}")
    if config.MESSAGE_QUEUE_TYPE == 'redis':
        url = config.REDIS_URL
        return RedisQueue(url, key=config.REDIS_QUEUE_KEY, *args, **kwargs)
    else:
        raise RuntimeError(f"Unknown message queue type: {config.QUEUE_TYPE}")
