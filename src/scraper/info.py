import re
import time
import logging

from common.time import twittertime as twittertime

class InfoScraper:
    def __init__(self, rlapi, userservice, scrapeservice):
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.userservice = userservice
    def main(self):
        try:
            rg = re.compile('[^A-z0-9#@.,;!\[\]]')

            while True:
                ids = []
                t = 15      # wait up to 15 seconds, otherwise we're behind on average

                while len(ids) < 100 and t > 0:
                    user_id = self.scrapeservice.dequeue('info')
                    if user_id and not self.scrapeservice.is_user_queued(user_id):
                        self.scrapeservice.mark_queued(user_id)
                    else:
                        time.sleep(1)
                        t = t - 1

                users_in_postgres = userservice.users_where('user_id in %s', [tuple(user_ids)])

                for user in users_in_postgres:
                    user_ids_set.discard(user['user_id'])

                logging.debug('Scraping info for %d users', len(ids))

                if len(ids) == 0:
                    continue

                resp = self.rlapi.request('users/lookup', {'user_id': ','.join(ids)})
                for user in resp.get_iterator():
                    if 'id' not in user:
                        continue

                    self.userservice.create_user({
                        'user_id': user['id_str'],
                        'screen_name': rg.sub('', user['screen_name']),
                        'total_tweets': user['statuses_count'],
                        'followers': user['followers_count'],
                        'following': user['friends_count'],
                        'full_name': rg.sub('', user['name']),
                        'bio': rg.sub('', user['description']),
                        'timestamp': twittertime(user['created_at'])
                    })

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))
