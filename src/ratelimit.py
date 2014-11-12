import time
import logging
import re

class RateLimitedTwitterAPI:
    def __init__(self, apis):
        if len(apis) == 0:
            raise Exception("Can't make a rate limited api from zero apis")
        self.apis = apis

    def request(self, resource, params=None, files=None):
        while True:
            for i in range(len(self.apis)):
                api = self.apis[i]
                overlimits = False
                sleep_time = 1

                while not overlimits:
                    try:
                        response = api.request(resource, params, files)
                    except Exception as e:
                        time.sleep(sleep_time)
                        sleep_time = sleep_time * 2 # exponential backoff
                        continue
                    if response.status_code == 429:
                        overlimits = True
                        continue
                    elif response.status_code >= 500:
                        time.sleep(sleep_time)
                        sleep_time = sleep_time * 2 # exponential backoff
                    elif response.status_code == 200:
                        return response
