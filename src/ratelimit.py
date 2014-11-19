import traceback
import time
import logging
import re
import json

from util import twittertime 

class RateLimitedTwitterAPI:
    def __init__(self, apis):
        self.apis = apis

    def request(self, resource, params=None):
        for i in range(len(self.apis)):
            overlimits = False

            while not overlimits:
                try:
                    response = self.apis[i].request(resource, params)
                except Exception as e:
                    logging.warn('Sleeping through Exception (because %s around %s)', e, traceback.format_exc())
                    continue

                if response.status_code == 401:
                    logging.warn('Got 401\n\n%s', str(response.json))
                    raise ProtectedException()
                elif response.status_code == 429:
                    logging.info('Over limits on %d %s', i, resource)
                    overlimits = True
                elif response.status_code >= 400 and response.status_code < 500:
                    logging.warn('Got 4xx error with client %d when requesting %s (%s)\n\n%s\n\n%s', i, resource, params, str(response.headers), str(response.text))
                elif response.status_code == 200:
                    self.api_numbers_per_endpoint[resource] = i
                    return response.json

                time.sleep(1)

        logging.warn('Raising because no clients worked.')
        raise Exception('All clients over limits')

class ProtectedException(Exception):
    def __init__(self):
        self.msg = "User is protected."
