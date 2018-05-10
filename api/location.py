from api.logging import log


def detect_location(tweet):
    """
    Detect the location where the tweet is posted.
    :param tweet:   the tweet object
    :return:        nothing, the tweet object will be updated inline
    """
    if tweet['place']:
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/geo-objects#place-dictionary
        if tweet['place']['place_type'] == 'city':
            if tweet['place']['country'] == 'United States':
                tweet['place']['city'] = tweet['place']['name']
                tweet['place']['state'] = tweet['place']['full_name'].split(',')[1].strip()
            else:
                # TODO: other countries have different formats to parse
                pass
        elif tweet['place']['place_type'] == 'admin':
            state = tweet['place']['full_name'].split(',')[1].strip()
            # TODO: convert state name to state code
        else:
            log.warn(f"Not handling the place with unknown type: {tweet['place']}")

        log.info(f"Detected location of tweet {tweet['id']}: {tweet['place']}")
    elif tweet['coordinates']:
        log.info(f"Trying to detect location based on coordinates: {tweet['coordinates']}")
        long, lat = tweet['coordinates']['coordinates']
        # TODO: reverse geocoding
