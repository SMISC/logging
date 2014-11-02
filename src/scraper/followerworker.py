import time
import logging

class FollowersScraperWorker:
    def __init__(self, rlapi, edgeservice, scrapeservice, evt):
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.edgeservice = edgeservice
        self.evt = evt
    def main(self):
        try:
            while not self.evt.is_set():
                time.sleep(5)
                user_id = self.scrapeservice.dequeue('follow')
                if not user_id:
                    continue

                logging.debug('Scraping followers for %d', int(user_id))
                cursor = -1
                while cursor <= 0:
                    resp = self.rlapi.request('followers/ids', {'user_id': user_id, 'count': 5000, 'cursor': cursor})
                    for follower in resp.get_iterator():
                        if 'ids' not in follower:
                            continue

                        resp_follower_ids = []
                        for follower_id in follower['ids']:
                            resp_follower_ids.append(str(follower_id))

                        self.edgeservice.add_follower_edges(user_id, resp_follower_ids)
                        cursor = follower['next_cursor']

                self.scrapeservice.finished(user['id_str'], 'follow')

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))

