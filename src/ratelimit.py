import traceback
import time
import logging
import re
import json

from util import twittertime 
from twitter import Twitter
from twitter import twitter_from_credentials

class RateLimitedTwitterAPI:
    def __init__(self, rds, credentials):
        self.api_per_key = dict()
        self.credentials = credentials
        self.rds = rds
        self.api_numbers_per_endpoint = dict()

    def _getIthClientLazily(self, i):
        (key, secret) = self.credentials[i]
        if key not in self.api_per_key:
            access_key = self.rds.get('access_key_%s' % (key))

            if access_key is None:
                self.api_per_key[key] = twitter_from_credentials(key, secret)
            else:
                self.api_per_key[key] = Twitter(access_key)

        return self.api_per_key[key]
        
    def request(self, resource, params=None):
        ''' TECHNICALLY WON'T WORK FOR RESOURCES WITH PLACEHOLDERS BUT WORKS FINE NOW'''
        if resource in self.api_numbers_per_endpoint:
            start_i = self.api_numbers_per_endpoint[resource]
        else:
            start_i = 0

        sequence = list(range(start_i, len(self.credentials)))
        sequence.extend(list(range(0, start_i)))

        for j in range(len(sequence)):
            i = sequence[j]
            try:
                api = self._getIthClientLazily(i)
            except Exception as e:
                logging.warn('Skipping %dth client (client-id: %s) that had an exception: %s', i, self.credentials[i][0], str(e))
                continue

            overlimits = False
            attempts = 0

            while not overlimits and attempts <= 3:
                attempts = attempts + 1
                try:
                    response = api.request(resource, params)
                except Exception as e:
                    logging.warn('Sleeping through Exception (because %s around %s)', e, traceback.format_exc())
                    continue

                logging.debug('status code %d', response.status_code)

                if response.status_code == 429:
                    overlimits = True
                    continue
                elif response.status_code == 401:
                    # tried to get protected resource
                    raise ProtectedException()
                elif response.status_code >= 400 and response.status_code < 500:
                    logging.warn('Got 4xx error with client %d (client-id %s) when requesting %s (%s)\n\n%s\n\n%s', i, self.credentials[i][0], resource, params, str(response.headers), str(response.text))
                elif response.status_code == 200:
                    self.api_numbers_per_endpoint[resource] = i
                    return json.loads(response.text)

        logging.warn('Raising because no clients worked.')
        raise Exception('All clients over limits')

            

class ProtectedException(Exception):
    def __init__(self):
        self.msg = "User is protected."
