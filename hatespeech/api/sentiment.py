# -*- coding: utf-8 -*-
import nltk
import pandas as pd
import dill as pickle
import re
from functools import partial
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split

from hatespeech.api.logging2 import log


# ============================================================================

BASE_PATH = './data/twitter-sentiment'
MODEL_PATH = BASE_PATH + '/model.pickle'
DATASET_PATH = BASE_PATH + '/sentiment.csv'
FEATURE_FUNC_PATH = BASE_PATH + '/feature_func.pickle'

CLASSIFIER = None
FEATURE_FUNC = None

SENTIMENT_MAP = {
    'Negative': 2,
    'Neutral': 1,
    'Positive': 0,
}

nltk.download('stopwords')
STOPWORDS = set(stopwords.words("english"))


# ============================================================================
# NOTE:
# The implementation takes inspiration from the idea found here:
# https://www.kaggle.com/ngyptr/python-nltk-sentiment-analysis/code

def _get_words_in_tweets(tweets):
    all = []
    for (words, sentiment) in tweets:
        all.extend(words)
    return all


def _get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    features = set(wordlist.keys())
    return features


def _extract_features(document, word_features=None):
    """
    Extract features from a document.

    :param document:        the original text in form of a list of words.
    :param word_features:   the list of all word features
    :return:                a dictionary of feature set
    """
    document_words = set(document)
    return dict(
        (word, (word in document_words))
        for word in word_features
    )


def _preprocess_text(text):
    """
    Perform text preprocessing.

    :param text:    the original text
    :return:        the preprocessed text
    """
    # text = re.sub(r'[^\x00-\x7f]', r'', text)   # remove non-ASCII characters
    text = re.sub(r'http\S+', '', text)         # remove URLs from text
    text = re.sub(r'#', '', text)               # consider hash tags as normal content
    text = _remove_punctuation(text)            # remove punctuations
    words = (word.lower() for word in text.split()
             if word not in STOPWORDS           # not a stop word
             and not word.startswith('@')       # don't take into account user mentions
             and word != 'RT'                   # no retweet notation
             )
    return list(words)


def _remove_punctuation(text):
    """
    Remove punctuation from a text.

    :param text:    the text input
    :return:        the text with punctuation removed
    """
    if not hasattr(_remove_punctuation, 'translator'):
        import string
        _remove_punctuation.translator = str.maketrans('', '', string.punctuation)

    return text.translate(_remove_punctuation.translator)


def train_and_test_classifier():
    """
    Train the Naive Bayes classifier and perform preliminary testing on it.
    The model and feature extracting function will be persisted to file.
    """
    # load the dataset and keep the necessary columns
    data = pd.read_csv(DATASET_PATH)
    data = data[['text', 'sentiment']]

    # split train-test data and arrange respective classes
    train, test = train_test_split(data, test_size=0.1)

    train_pos = train[train['sentiment'] == 'Positive']
    train_pos = train_pos['text']
    train_neg = train[train['sentiment'] == 'Negative']
    train_neg = train_neg['text']
    train_neu = train[train['sentiment'] == 'Neutral']
    train_neu = train_neu['text']

    test_pos = test[test['sentiment'] == 'Positive']
    test_pos = test_pos['text']
    test_neg = test[test['sentiment'] == 'Negative']
    test_neg = test_neg['text']
    test_neu = test[test['sentiment'] == 'Neutral']
    test_neu = test_neu['text']

    log.info(f"Train data: {len(train_pos)} positive, {len(train_neg)} negative, {len(train_neu)} neutral")
    log.info(f"Test data: {len(test_pos)} positive, {len(test_neg)} negative, {len(test_neu)} neutral")

    # text pre-processing
    tweets = [(_preprocess_text(row.text), row.sentiment) for index, row in train.iterrows()]

    # extract word features
    word_features = _get_word_features(_get_words_in_tweets(tweets))
    extract_features = partial(_extract_features, word_features=word_features)
    log.info(f"{len(word_features)} feature(s): {word_features[:1000]}")

    # persist the feature extraction function to file
    with open(FEATURE_FUNC_PATH, 'wb') as f:
        pickle.dump(extract_features, f)

    # train the classifier
    training_set = nltk.classify.apply_features(extract_features, tweets)
    classifier = nltk.NaiveBayesClassifier.train(training_set)
    classifier.show_most_informative_features(20)

    # persist the classifier to file
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(classifier, f)

    neg_cnt = 0
    pos_cnt = 0
    neu_cnt = 0
    for obj in test_neg:
        res = classifier.classify(extract_features(obj.split()))
        if res == 'Negative':
            neg_cnt += 1
    for obj in test_neu:
        res = classifier.classify(extract_features(obj.split()))
        if res == 'Neutral':
            neu_cnt += 1
    for obj in test_pos:
        res = classifier.classify(extract_features(obj.split()))
        if res == 'Positive':
            pos_cnt += 1

    log.info(f"Negative: {neg_cnt}/{len(test_neg)} [{neg_cnt/len(test_neg)*100.0}%]")
    log.info(f"Neutral: {neu_cnt}/{len(test_neu)} [{neu_cnt/len(test_neu)*100.0}%]")
    log.info(f"Positive: {pos_cnt}/{len(test_pos)} [{pos_cnt/len(test_pos)*100.0}%]")


def classify(tweet):
    """
    Analyse the sentiment level of a tweet.

    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    global CLASSIFIER, FEATURE_FUNC
    text = _preprocess_text(tweet['text'])
    extract_features = FEATURE_FUNC
    sentiment = CLASSIFIER.classify(extract_features(text))
    sentiment = SENTIMENT_MAP.get(sentiment)
    tweet['sentiment'] = sentiment


def load_classifier():
    """
    Load the classifier model from disk.
    """
    global CLASSIFIER, FEATURE_FUNC
    if not CLASSIFIER or not FEATURE_FUNC:
        with open(MODEL_PATH, 'rb') as f:
            CLASSIFIER = pickle.load(f)

        with open(FEATURE_FUNC_PATH, 'rb') as f:
            FEATURE_FUNC = pickle.load(f)


def init():
    """
    Initialize the sentiment analyser.
    This method must be called before any usage of this module.
    """
    try:
        log.info("Loading pre-trained classifier for sentiment analysis")
        load_classifier()
    except FileNotFoundError:
        log.info("Not found pre-trained classifier. Will train a new one")
        train_and_test_classifier()
        try:
            load_classifier()
        except Exception:
            log.exception("Unable to train and test new classifier. Sentiment analysis will not work")
            return
    except Exception:
        log.exception("Unable to load the classifier. Sentiment analysis will not work")
        return

    log.info("Loaded pre-trained classifier for sentiment analysis")


if __name__ == '__main__':
    init()


