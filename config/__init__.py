import json
import os


_CONFIG_FILE = 'keys.json'
_CONFIG = None

# TODO: handle possible exceptions
with open(_CONFIG_FILE, 'r') as f:
    _CONFIG = json.load(f)


# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class dotdict(dict):
    """Dictionary with dot notation access."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Config:
    SECRET_KEY = 'testkey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HATE_WORD_LIST_FILE = _CONFIG['HATE_WORD_LIST_FILE']


class DevelopmentConfig(Config):
    MONGO_URI = 'mongodb://localhost:27017/twitter'
    DEBUG = True

    TWITTER = dotdict({
        'CONSUMER_KEY': _CONFIG['TWITTER']['CONSUMER_KEY'],
        'CONSUMER_SECRET': _CONFIG['TWITTER']['CONSUMER_SECRET'],
        'ACCESS_TOKEN': _CONFIG['TWITTER']['ACCESS_TOKEN'],
        'ACCESS_SECRET': _CONFIG['TWITTER']['ACCESS_SECRET'],
    })


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG = False


class DockerDevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://testusr:password@postgres/testdb'
    DEBUG = True


# TODO: implement memoization to avoid recalculation
def _config():
    return {
        'dev': DevelopmentConfig,
        'prod': ProductionConfig,
        'docker': DockerDevConfig
    }[os.environ.get('FLASK_ENV', 'dev')]


config = _config()