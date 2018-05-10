from bson import json_util
import json
import tweepy
from api import app, hatespeech, gender, logging, location
from api.database import mongo
from flask import Blueprint, jsonify

log = logging.log

mod = Blueprint('twitter', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation


@app.route('/tweets')
def tweets():
    """Return all tweets from database that has been processed."""
    result = mongo.db.result.find()
    return jsonify(result=[
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in result
    ])

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

    def on_limit(self, track):
        log.info(f"Tracking info: {track}")

    def on_data(self, raw_data):
        try:
            data = json.loads(raw_data)

            # The data is not always a tweet but can also be a message from Twitter system itself
            if 'limit' in data:
                return self.on_limit(data)
            elif 'text' not in data:
                log.warn(f"Unknown message type: {data}")
                # TODO: what to do with unknown message?
                with app.app_context():
                    mongo.db.unknown.insert(data)
                return


            tweet = data

            # save original tweet to database
            with app.app_context():
                mongo.db.tweet.insert(tweet)

            self._preprocess(tweet)

            with app.app_context():
                mongo.db.result.insert(tweet)
        except Exception as e:
            log.exception("Exception on processing tweet")

        # TODO: remove
        # return False

    def _preprocess(self, tweet):
        # TODO: implementation
        text = tweet['text']

        text = text.lower()
        text = remove_punctuation(text)
        words = text.split()
        tweet['text'] = words

        gender.detect_gender(tweet)
        location.detect_location(tweet)
        analyse_sentiment(tweet)


class Stream(tweepy.Stream):

    def __init__(self, auth, listener, **options):
        super().__init__(auth, listener, **options)

    def start(self):
        """Start or resume the streaming if it's been stopped before."""
        log.info("Start listening for tweets data")
        # TODO: set the stream parameters correctly
        self.filter(
            track=hatespeech.get_hate_word_list(),
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
    if not hasattr(remove_punctuation, 'translator'):
        import string
        remove_punctuation.translator = str.maketrans('', '', string.punctuation)

    return text.translate(remove_punctuation.translator)


def analyse_sentiment(tweet):
    """
    Perform sentiment analysis of the tweet
    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    # TODO: implementation
    import random
    tweet['sentiment_level'] = random.randint(0, 5)