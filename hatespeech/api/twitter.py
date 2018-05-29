import functools
import json
import pymongo
import tweepy
from hatespeech.api import app, hateword, gender, location
from hatespeech.api.database import mongo
from hatespeech.api.logging2 import log
from hatespeech.api.utils import safe_get, safe_get_dict
from hatespeech.config import config
from bson import json_util
from datetime import datetime
from flask import Blueprint, Response, jsonify, request, \
    copy_current_request_context, stream_with_context


mod = Blueprint('twitter', __name__)

# ============================================================================
# API for managing and using tweet data
# TODO: implementation


@app.route('/tweets')
def tweets():
    """
    Return tweets from database that has been processed from the latest one.

    :param limit:   limit the number of result to be returned
    """
    limit = int(request.args.get('limit', 0))

    result = mongo.db.result.find()\
        .sort('$natural', pymongo.DESCENDING)\
        .limit(limit)
    return jsonify(result=[
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in result
    ])


@app.route('/tweets/export')
def export_tweets():
    """
    Export all results as CSV file from the latest tweet.

    :param limit:   limit the number of result to be returned
    """
    @copy_current_request_context
    def generate():
        import io, csv
        output = io.StringIO()
        writer = csv.DictWriter(output, dialect='unix', fieldnames=[
            "id",
            "timestamp",
            "text",
            "hashtags",
            # "reply_to",
            # "mention",
            "keywords",
            "gender",
            "longitude",
            "latitude",
            "city",
            "state",
            "country_code",
            "sentiment_level",
        ])

        writer.writeheader()
        output.seek(0)
        yield output.read()
        output.truncate(0)

        # helper functions to retrieve coordinates
        get_long = lambda tweet: safe_get(safe_get_dict(tweet, ['coordinates', 'coordinates'] ,default=[]), 0, '')
        get_lat = lambda tweet: safe_get(safe_get_dict(tweet, ['coordinates', 'coordinates'] ,default=[]), 1, '')

        # the number of result to get
        limit = int(request.args.get('limit', 0))

        for tweet in mongo.db.result.find()\
                .sort('$natural', pymongo.DESCENDING)\
                .limit(limit):
            writer.writerow({
                'id': tweet['id'],
                'timestamp': tweet['timestamp'],
                'text': tweet['text'],
                'hashtags': ','.join(tweet['entities'].get('hashtags', [])),
                # reply to
                # mention
                'keywords': ','.join(tweet.get('keywords', [])),
                'gender': tweet.get('gender', ''),
                'longitude': get_long(tweet),
                'latitude': get_lat(tweet),
                'city': safe_get_dict(tweet, ['place', 'city'], ''),
                'state': safe_get_dict(tweet, ['place', 'state'], ''),
                'country_code': safe_get_dict(tweet, ['place', 'country_code'], ''),
                'sentiment_level': tweet.get('sentiment_level', ''),
            })
            output.seek(0)
            yield output.read()
            output.truncate(0)

    response = Response(stream_with_context(generate()),
                        mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=result.csv'
    return response


@app.route('/tweets/filter/date', methods=['POST'])
def filter_tweets_by_date():
    """
    Retrieve tweets by start and end dates.
    """
    req = request.get_json(force=True)
    start_date = req.get('start_date')
    end_date = req.get('end_date')

    try:
        # ensure that the specified time is in UTC +0000
        date_format = '%d/%m/%Y %z'
        start_date = datetime.strptime(start_date + " +0000", date_format).timestamp() * 1000
        end_date = datetime.strptime(end_date + " +0000", date_format).timestamp() * 1000

        if start_date >= end_date:
            raise Exception("End date is equal to or earlier than start date")
    except Exception:
        log.exception("Date(s) are invalid")
        return Response("Date(s) are invalid", status=400)

    result = mongo.db.result.find({'timestamp_ms': {'$gte': start_date, '$lt': end_date}})

    return jsonify(result=[
        json.loads(json.dumps(item, indent=4, default=json_util.default))
        for item in result
    ])


@app.route('/tweets/search', methods=['POST'])
def search_tweets():
    # TODO: implementation
    req = request.get_json(force=True)
    keyword = req.get('keyword')
    limit = int(req.get('limit', 1000))

    if not keyword:
        return Response("Keyword is not specified", 400)

    api = _get_api()
    result = (_preprocess(tweet._json) for tweet in tweepy.Cursor(api.search, q=keyword, count=limit).items(limit))
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

            tweet = _preprocess(data)

            with app.app_context():
                mongo.db.result.insert(tweet)
        except Exception as e:
            log.exception("Exception on processing tweet")

        # TODO: remove
        # return False


class Stream(tweepy.Stream):

    def __init__(self, auth, listener, **options):
        super().__init__(auth, listener, **options)

    def start(self):
        """Start or resume the streaming if it's been stopped before."""
        log.info("Start listening for tweets data")
        # TODO: set the stream parameters correctly
        self.filter(
            track=hateword.get_hate_word_list(),
            languages=['en'],
            async=True)

    def stop(self):
        """Pause the streaming process."""
        log.info("Stopping the stream")
        # NOTE: this will stop after the next tweet arrives
        self.running = False


def _get_api():
    """
    Return the Twitter's API object.
    """
    auth = tweepy.OAuthHandler(
        consumer_key=config.TWITTER.CONSUMER_KEY,
        consumer_secret=config.TWITTER.CONSUMER_SECRET)
    auth.set_access_token(
        config.TWITTER.ACCESS_TOKEN,
        config.TWITTER.ACCESS_SECRET)
    api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True)
    return api


def create_stream():
    """
    Create a stream that listens for tweets from Twitter.
    """
    api = _get_api()
    listener = StreamListener(api=api)
    stream = Stream(auth=api.auth, listener=listener)

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


def _preprocess(tweet):
    """
    Perform pre-processing of tweet data.
    :param tweet:   the tweet object
    :return:        a new tweet object
    """
    try:
        if tweet.get('truncated') and tweet.get('extended_tweet'):
            full_text = tweet['extended_tweet']['full_text']
            tweet['text'] = full_text

        if not tweet.get('timestamp_ms'):
            datetime_format = '%a %b %d %H:%M:%S %z %Y'
            tweet['timestamp_ms'] = datetime.strptime(tweet['created_at'], datetime_format).timestamp() * 1000

        hash_tags = [i['text'] for i in tweet['entities'].get('hashtags', [])]
        user_mentions = [{
            'screen_name': i['screen_name'],
            'name': i['name'],
            'id': i['id_str'],
        } for i in tweet['entities'].get('user_mentions', [])]

        gender.detect_gender(tweet)
        location.detect_location(tweet)
        analyse_sentiment(tweet)

        return {
            'id': tweet['id_str'],
            'user': {
                'id': tweet['user']['id_str'],
                'name': tweet['user']['name'],
                'screen_name': tweet['user']['screen_name'],
                'gender':tweet['user']['gender'],
            },
            'timestamp': tweet['created_at'],
            'timestamp_ms': int(tweet['timestamp_ms']),
            'text': tweet['text'],
            'coordinates': tweet.get('coordinates'),
            'place': {
                'city': safe_get_dict(tweet, ['place', 'city']),
                'state': safe_get_dict(tweet, ['place', 'state']),
                'country_code': safe_get_dict(tweet, ['place', 'country_code']),
            },
            'keywords': None, # TODO
            'reply_to': None, # TODO
            'entities': {
                'hashtags': hash_tags,
                'user_mentions': user_mentions,
            },
        }
    except Exception as e:
        log.exception(f"Error during processing tweet [${tweet['id']}]")