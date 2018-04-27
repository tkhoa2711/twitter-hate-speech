import logging
import tweepy
from api import app
from flask import Blueprint
from . import hatespeech

log = logging.getLogger(__name__)

mod = Blueprint('twitter', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation

@app.route('/tweets')
def tweets():
    """Return all tweets from database."""
    pass


@app.route('/tweets/<id>')
def tweet(id):
    """Retrieve a tweet given its ID."""
    pass

# ============================================================================
# Functionality to work with Twitter

class StreamListener(tweepy.StreamListener):

    def start(self):
        """Start or resume the streaming if it's been stopped before."""
        pass

    def stop(self):
        """Pause the streaming process."""
        pass

    def on_connect(self):
        log.info("Connected to Twitter streaming API")

    def on_error(self, status_code):
        log.error('Error: ' + repr(status_code))
        if status_code == 420:
            return False

        # returning non-False reconnects the stream, with backoff
        # TODO: should we do anything else

    def on_data(self, raw_data):
        log.debug(raw_data)

        # TODO: extract data

        # TODO: perform preproccessing

        # TODO: save tweet to database

        return False


def create_stream(config):
    """
    Create a stream that listens for tweets from Twitter.
    """
    auth = tweepy.OAuthHandler(
        consumer_key=config.TWITTER.CONSUMER_ACCESS,
        consumer_secret=config.TWITTER.CONSUMER_SECRET)
    auth.set_access_token(
        config.TWITTER.ACCESS_TOKEN,
        config.TWITTER.ACCESS_SECRET)
    listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = tweepy.Stream(auth=auth, listener=listener)

    # TODO: set the stream parameters correctly
    stream.filter(
        track=hatespeech.get_hate_word_list(),
        # locations=[-122.75,36.8,-121.75,37.8,-74,40,-73,41], # San Francisco | New York
        languages=['en'],
        async=True)

    # TODO: implement a mechanism to stop the stream on-demand
    # HINT: return false either in on_data() or on_status()

    return stream
