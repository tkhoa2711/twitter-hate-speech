def detect_gender(tweet):
    """
    Detect the gender of the tweet's author.
    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    # TODO: implementation
    import random
    tweet['user']['gender'] = random.choice(['M', 'F', 'NA'])
