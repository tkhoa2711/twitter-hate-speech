import re
from api.app import app
from gender_predictor import GenderPredictor


# ============================================================================

log = app.logger

# setup the gender predictor
log.info("Setting up gender predictor")
gp = GenderPredictor()
gp.train_and_test()


# ============================================================================

def detect_gender(tweet):
    """
    Detect the gender of the tweet's author.
    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    orig_name = tweet['user']['name']
    name = re.sub(r'[^\x00-\x7f]', r'', orig_name)   # remove non-ASCII characters
    gender = 'NA'

    try:
        first_name = extract_first_name(name)

        global gp
        gender = gp.classify(first_name)
    except IndexError:
        # first name is most likely empty in this case
        # probably due to the name containing non-standard characters
        pass
    except Exception:
        log.exception("Unable to detect gender based on first name")
        pass

    tweet['user']['gender'] = gender
    log.debug(f'Name: {orig_name} - First name: {first_name} - Gender: {gender}')


def extract_first_name(name):
    """
    Extract the first name from the Twitter user's name,
    which is not necessarily a person's name.

    :param name:    the name of the Twitter user as defined by him or her
    :return:        the probable first name
    """
    # NOTE: Here we are assuming that the name is written in conventional format.
    # However, in reality, the display name is present in various format.
    # Future work should take this into account
    try:
        first_name = name.split(' ', 1)[0]
        return first_name
    except Exception:
        raise Exception(f'Unable to extract first name from [{name}]')
