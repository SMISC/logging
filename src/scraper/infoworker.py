import threading
import re
import time
import logging

from ratelimit import ProtectedException
from util import twittertime as twittertime

class InfoScraperWorker(threading.Thread):
    def __init__(self, rlapi, userservice, scrapeservice):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.userservice = userservice
    def run(self):
        try:
            rg = re.compile('[^ A-z0-9#@.,;!\[\]]')

            user_ids = []
            t = 15      # wait up to 15 seconds, otherwise we're behind on average

            while len(user_ids) < 100 and t > 0:
                user_id = self.scrapeservice.dequeue()

                if user_id:
                    user_ids.append(user_id)
                else:
                    time.sleep(1)
                    t = t - 1

            logging.debug('Acquired %d users', len(user_ids))

            if len(user_ids) == 0:
                return

            resp = self.rlapi.request('users/lookup', {'user_id': ','.join(user_ids)})
            for user in resp:
                if 'profile_banner_url' in user:
                    pbu = user['profile_banner_url']
                else:
                    pbu = None

                if 'profile_image_url' in user:
                    piu = user['profile_image_url']
                else:
                    piu = None

                ts = None

                try:
                    ts = twittertime(user['created_at'])
                except Exception as e:
                    logging.warn("Caught error when parsing timestamp (%s): %s", user['created_at'], str(e))

                self.userservice.create_user({
                    'user_id': user['id_str'],
                    'screen_name': rg.sub('', user['screen_name']),
                    'total_tweets': user['statuses_count'],
                    'followers': user['followers_count'],
                    'following': user['friends_count'],
                    'full_name': rg.sub('', user['name']),
                    'bio': rg.sub('', user['description']),
                    'timestamp': ts,
                    'interesting': True,
                    'location': user['location'],
                    'website': user['url'],
                    'profile_image_url': piu,
                    'profile_banner_url': pbu,
                    'protected': user['protected']
                })

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))
