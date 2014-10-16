import time
import logging
import re

class RateLimitedTwitterAPI:
    # to make this thread wake up early, call `event`.set()
    def __init__(self, api, wakeup):
        self.limits = None
        self.api = api
        self.wakeup = wakeup

    def request(self, resource, params=None, files=None):
        if self.limits is not None:
            self.block_until_available(resource)
        if not self.wakeup.is_set():
            response = self.api.request(resource, params, files)
            logging.debug('API response code: %d', response.status_code)
            if (response.status_code) == 429:
                quota = response.get_rest_quota()
                logging.debug('REST quota: %s', str(quota))
                if self.limits is not None and quota['reset'] is not None:
                    self.updateWith(resource, quota)
                self.block_until_available(resource)
                if self.wakeup.is_set(): # timed out
                    raise EOFError, "waking up..."
            return response
        # timed out
        return None

    def flatten(self, response):
        limits_flattened = {}
        for limits in response.get_iterator():
            for (category, items) in limits['resources'].items():
                for (uri, limit) in items.items():
                    uri_parts = uri.split('/')
                    re_parts = []
                    for part in uri_parts:
                        if 0 == len(part):
                            continue
                        if part[0] == ':':
                            re_parts.append('.*')
                        else:
                            re_parts.append(part)
                    re_text = '^' + ('/'.join(re_parts)) + '$'
                    limits_flattened[uri] = {
                        'limit': limit,
                        'regex': re.compile(re_text)
                    }
        return limits_flattened

    def set_rate_limits(self, limits):
        self.limits = self.flatten(limits)

    def _get_uri_pattern(self, uri):
        for (uri_pattern, limit_mask) in self.limits.items():
            if limit_mask['regex'].match(uri):
                return uri_pattern

    def decrement(self, uri):
        uri_pattern = self._get_uri_pattern(uri)
        self.limits[uri_pattern]['limit']['remaining'] -= 1

    def update(self):
        rate_limits = self.api.request('application/rate_limit_status')
        self.set_rate_limits(rate_limits)

    def updateWith(self, uri, data):
        uri_pattern = self._get_uri_pattern(uri)
        data['reset'] = int(data['reset'].timestamp())
        self.limits[uri_pattern]['limit'] = data

    def get_limit_info(self, uri):
        uri_pattern = self._get_uri_pattern(uri)
        return self.limits[uri_pattern]['limit']

    def block_until_available(self, uri):
        while True:
            limit = self.get_limit_info(uri)
            now = int(time.time())
            if limit['remaining'] > 0 or limit['reset'] <= now:
                break
            while limit['remaining'] <= 0 and limit['reset'] > now:
                time_to_sleep = limit['reset'] - now
                logging.debug('%d seconds left on %s rate limit' % (time_to_sleep, uri))
                if self.wakeup.wait(min(10, time_to_sleep)):
                    return
                now = int(time.time())
            self.update()
