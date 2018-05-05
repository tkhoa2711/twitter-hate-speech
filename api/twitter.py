import json
import logging
import tweepy
from api import app
from api.database import mongo
from flask import Blueprint
from api import hatespeech

# log = app.logger
log = logging.getLogger(__name__)

mod = Blueprint('twitter', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation


@app.route('/tweets')
def tweets():
    """Return all tweets from database that has been processed."""
    pass

# ============================================================================
# Functionality to work with Twitter

class StreamListener(tweepy.StreamListener):

    def on_connect(self):
        log.info("Connected to Twitter streaming API")

    def on_error(self, status_code):
        log.error('Error status: ' + repr(status_code))
        if status_code == 420:
            return False

        # returning non-False reconnects the stream, with backoff
        # TODO: should we do anything else

    def on_data(self, raw_data):
        tweet = json.loads(raw_data)
        log.info(tweet)

        # save original tweet to database
        with app.app_context():
            mongo.db.tweet.insert(tweet)

        # TODO: extract data
        # tweet = {
        #     'id': data['id'],
        #     'text': data['text'],
        #     'user': {
        #         'id': data['user']['id_str'], # use string format because the number representation is larger than 53 bits
        #         'name': data['user']['name'],
        #         # 'screen_name': data['user']['screen_name'],
        #     },
        #     # 'place': data['place'], # indicates that the tweet is associated (but not necessarily originating from) a place
        #     'coordinates': data['coordinates'],
        #     # 'timestamp_ms': data['timestamp_ms'], # TODO: which one to use?
        #     'created_at': data['created_at'],
        # }

        # TODO: perform preproccessing
        self._preprocess(tweet)

        # TODO: save result to database
        with app.app_context():
            mongo.db.result.insert(tweet)

        # TODO: remove
        return False

    def _preprocess(self, tweet):
        # TODO: implementation
        text = tweet['text']

        text = text.lower()
        text = remove_punctuation(text)
        words = text.split()
        tweet['text'] = words

        detect_gender(tweet)
        detect_location(tweet)


class Stream(tweepy.Stream):

    def __init__(self, auth, listener, **options):
        super().__init__(auth, listener, **options)

    def start(self):
        """Start or resume the streaming if it's been stopped before."""
        log.info("Start listening for tweets data")
        # TODO: set the stream parameters correctly
        self.filter(
            # track=hatespeech.get_hate_word_list(),
            track=['hate', 'black'],
            # locations=[-122.75,36.8,-121.75,37.8,-74,40,-73,41], # San Francisco | New York
            languages=['en'],
            async=True)

    def stop(self):
        """Pause the streaming process."""
        log.info("Stopping the stream")
        # NOTE: this will stop after the next tweet arrives
        self.running = False


def create_stream(config):
    """
    Create a stream that listens for tweets from Twitter.
    """
    auth = tweepy.OAuthHandler(
        consumer_key=config.TWITTER.CONSUMER_KEY,
        consumer_secret=config.TWITTER.CONSUMER_SECRET)
    auth.set_access_token(
        config.TWITTER.ACCESS_TOKEN,
        config.TWITTER.ACCESS_SECRET)
    listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    stream = Stream(auth=auth, listener=listener)

    # TODO: implement a mechanism to stop the stream on-demand
    # HINT: return false either in on_data() or on_status()

    return stream

# ============================================================================
# Helper function


def remove_punctuation(text):
    """
    Remove punctuation from a text.
    :param text:    the text input
    :return:        the text with punctuation removed
    """
    if not remove_punctuation.translator:
        import string
        remove_punctuation.translator = str.maketrans('', '', string.punctuation)

    return text.translate(remove_punctuation.translator)


def detect_gender(tweet):
    """
    Detect the gender of the tweet's author.
    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    # TODO: implementation
    pass


def detect_location(tweet):
    """
    Detect the location where the tweet is posted.
    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    # TODO: implementation
    pass