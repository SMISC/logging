import re
import time
import logging

class InfoScraperWorker:
    def __init__(self, rlapi, userservice, scrapeservice, evt):
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.userservice = userservice
        self.evt = evt
    def main(self):
        try:
            rg = re.compile('[^A-z0-9#@.,;!\[\]]')

            while not self.evt.is_set():
                user_ids = []
                t = 15      # wait up to 15 seconds, otherwise we're behind on average

                while len(user_ids) < 100 and t > 0:
                    logging.debug('Accumulated %d users...' % (len(user_ids)))

                    user_id = self.scrapeservice.dequeue('info')
                    if user_id and not self.scrapeservice.is_user_queued(user_id):
                        self.scrapeservice.mark_queued(user_id)
                        user_ids.append(user_id)
                    else:
                        time.sleep(1)
                        t = t - 1

                if len(user_ids) == 0:
                    continue

                user_ids_set = set(user_ids)
                users_in_postgres = self.userservice.users_where('user_id in %s', [tuple(user_ids)])

                for user in users_in_postgres:
                    user_ids_set.discard(user['user_id'])

                user_ids = list(user_ids_set)

                logging.debug('Scraping info for %d users', len(user_ids))

                resp = self.rlapi.request('users/lookup', {'user_id': ','.join(user_ids)})
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
