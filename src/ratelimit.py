from TwitterAPI import TwitterAPI

import traceback
import time
import logging
import re

from util import twittertime 

class RateLimitedTwitterAPI:
    def __init__(self, credentials):
        self.api_per_key = dict()
        self.credentials = credentials
        self.api_numbers_per_endpoint = dict()

    def _getIthClientLazily(self, i):
        (key, secret) = self.credentials[i]
        if key not in self.api_per_key:
            self.api_per_key[key] = TwitterAPI(key, secret, auth_type='oAuth2')

        return self.api_per_key[key]
        
    def request(self, resource, params=None, files=None):
        cycle_sleep_base = 30
        cycle_sleep = cycle_sleep_base

        ''' TECHNICALLY WON'T WORK FOR RESOURCES WITH PLACEHOLDERS BUT WORKS FINE NOW'''
        if resource in self.api_numbers_per_endpoint:
            start_i = self.api_numbers_per_endpoint[resource]
        else:
            start_i = 0

        sequence = list(range(start_i, len(self.credentials)))
        sequence.extend(list(range(0, start_i)))

        while True:
            for j in range(len(sequence)):
                i = sequence[j]
                api = self._getIthClientLazily(i)
                overlimits = False
                sleep_time = 1

                while not overlimits:
                    try:
                        response = api.request(resource, params, files)
                    except Exception as e:
                        logging.warn('Sleeping through Exception %d (because %s around %s)', sleep_time, e, traceback.format_exc())
                        time.sleep(sleep_time)
                        sleep_time = sleep_time * 2 # exponential backoff
                        continue

                    logging.debug('status code %d', response.status_code)

                    if response.status_code == 429:
                        overlimits = True
                        continue
                    elif response.status_code >= 500:
                        time.sleep(sleep_time)
                        sleep_time = sleep_time * 2 # exponential backoff
                    elif response.status_code == 200:
                        self.api_numbers_per_endpoint[resource] = i
                        return response

            logging.info('All clients over limits. Sleeping for %d', cycle_sleep)
            time.sleep(cycle_sleep)
            cycle_sleep += cycle_sleep_base # linear backoff
