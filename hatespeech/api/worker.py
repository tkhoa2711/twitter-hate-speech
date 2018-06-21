import redis
from hatespeech.config import config
from hatespeech.api.logging2 import log
from hatespeech.api.twitter import process
import dill as pickle


def start_worker():
    r = redis.from_url(config.REDIS_URL)
    log.info("Started listening for message")
    while 1:
        try:
            msg = r.blpop(config.REDIS_QUEUE_KEY)[1]
            tweet = pickle.loads(msg)
            process(tweet)
        except Exception:
            log.exception(f"Error during execution")
