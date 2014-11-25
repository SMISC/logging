import traceback
import time
import logging
import re
import json

from util import twittertime 

logger = logging.getLogger(__name__)

class RateLimitedTwitterAPI:
    def __init__(self, apis):
        self.apis = apis

    def request(self, resource, params=None):
        for i in range(len(self.apis)):
            overlimits = False

            eb = 2

            while not overlimits:
                try:
                    response = self.apis[i].request(resource, params)
                except Exception as e:
                    logger.warn('Sleeping through Exception (because %s around %s)', e, traceback.format_exc())
                    time.sleep(eb)
                    eb = min(64, eb * 2)
                    continue

                if response.status_code == 401:
                    logger.warn('Got 401\n\n%s', str(response.json))
                    raise ProtectedException()
                elif response.status_code == 404:
                    raise NotFound()
                elif response.status_code == 429:
                    overlimits = True
                elif response.status_code >= 400 and response.status_code < 500:
                    logger.warn('Got 4xx error with client %d when requesting %s (%s)\n\n%s\n\n%s', i, resource, params, str(response.headers), str(response.text))
                elif response.status_code == 200:
                    return response.json

                time.sleep(1)

        logger.exception('Raising because no clients worked for %s (%s)', resource, params)
        raise OverLimits()

class NotFound(Exception):
    def __init__(self):
        self.msg = "Entity not found (404)"

class OverLimits(Exception):
    def __init__(self):
        self.msg = "All over limits"

class ProtectedException(Exception):
    def __init__(self):
        self.msg = "User is protected."
