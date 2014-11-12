from TwitterAPI import TwitterAPI

import time
import logging
import re

class RateLimitedTwitterAPI:
    def __init__(self, credentials):
        self.api_per_key = dict()
        self.credentials = credentials

    def _getIthClientLazily(self, i):
        (key, secret) = self.credentials[i]
        if key not in self.api_per_key:
            self.api_per_key[key] = TwitterAPI(key, secret, auth_type='oAuth2')

        return self.api_per_key[key]
        
    def request(self, resource, params=None, files=None):
        cycle_sleep_base = 30
        cycle_sleep = cycle_sleep_base

        while True:
            for i in range(len(self.credentials)):
                api = self._getIthClientLazily(i)
                overlimits = False
                sleep_time = 1

                while not overlimits:
                    try:
                        logging.debug("Requesting %s using the %dth client", resource, i)
                        response = api.request(resource, params, files)
                    except Exception as e:
                        logging.debug('Sleeping %d (because %s)', sleep_time, e)
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
                        return response

            logging.info('All clients over limits. Sleeping for %d', cycle_sleep)
            time.sleep(cycle_sleep)
            cycle_sleep += cycle_sleep_base # linear backoff
