import os
from dotenv import load_dotenv
from pathlib import Path

# load environment variables
env_path = Path('.') / '.env'
load_dotenv(verbose=True, dotenv_path=str(env_path))


# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class dotdict(dict):
    """Dictionary with dot notation access."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Config:
    SECRET_KEY = 'testkey'
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/twitter')
    PORT = int(os.environ.get('PORT', 5000))
    LOG_FILE = os.environ.get('LOG_FILE', './log.log')
    DISK_FREE_THRESHOLD = float(os.environ.get('DISK_FREE_THRESHOLD',  1.0))
    TWEET_STORE_MAX_SIZE = float(os.environ.get('TWEET_STORE_MAX_SIZE', 0)) * (2**20)

    TWITTER = dotdict({
        'CONSUMER_KEY': os.environ.get('TWITTER_CONSUMER_KEY', ''),
        'CONSUMER_SECRET': os.environ.get('TWITTER_CONSUMER_SECRET', ''),
        'ACCESS_TOKEN': os.environ.get('TWITTER_ACCESS_TOKEN', ''),
        'ACCESS_SECRET': os.environ.get('TWITTER_ACCESS_SECRET', ''),
    })


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class DockerDevConfig(Config):
    DEBUG = True


# TODO: implement memoization to avoid recalculation
def _config():
    return {
        'dev': DevelopmentConfig,
        'prod': ProductionConfig,
        'docker': DockerDevConfig
    }[os.environ.get('FLASK_ENV', 'dev')]


config = _config()