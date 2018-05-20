from api.logging import log
from statistics import mean


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
                # NOTE: other countries have different formats to parse
                # some have full_name as <city, state>, while others are <city, country>
                # at the moment, we have to assume that the 2nd element of full_name is state
                tweet['place']['city'] = tweet['place']['name']
                tweet['place']['state'] = tweet['place']['full_name'].split(',')[1].strip()
        elif tweet['place']['place_type'] == 'admin':
            tweet['place']['city'] = None
            tweet['place']['state'] = tweet['place']['name']
            # TODO: convert state name to state code
        elif tweet['place']['place_type'] == 'country':
            # only country info is available, nothing else we can do here
            tweet['place']['city'] = None
            tweet['place']['state'] = None
        else:
            log.warn(f"Not handling the place with unknown type: {tweet['place']}")

        # If the exact location of the tweet is not available, try to produce an approximate coordinates
        # by calculating the central point of the bounding box of the given place
        if not tweet['coordinates']:
            avg_long, avg_lat = [mean(lst) for lst in zip(*tweet['place']['bounding_box']['coordinates'][0])]
            tweet['coordinates'] = {
                'type': 'Point',
                'coordinates': [avg_long, avg_lat],
                'generated': True,
            }
        log.info(f"Detected location of tweet {tweet['id']} - coordinates: {tweet['coordinates']} - place: {tweet['place']}")
    elif tweet['coordinates']:
        log.info(f"Received tweet with coordinates: {tweet['coordinates']}")
        long, lat = tweet['coordinates']['coordinates']
        # TODO: reverse geocoding
