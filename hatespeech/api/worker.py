from hatespeech.api.logging2 import log
from hatespeech.api.mq import connect_to_message_queue
from hatespeech.api.twitter import process


def start_worker():
    q = connect_to_message_queue()
    log.info("Started listening for message")
    while 1:
        try:
            tweet = q.pop()
            process(tweet)
        except Exception:
            log.exception(f"Error during execution")
