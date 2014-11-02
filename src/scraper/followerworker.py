import time
import threading
import logging

class FollowersScraperWorker(threading.Thread):
    def __init__(self, rlapi, edgeservice, scrapeservice, evt):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.edgeservice = edgeservice
        self.evt = evt
    def run(self):
        try:
            edges = 0
            i = 0
            while not self.evt.is_set():
                time.sleep(1)
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
                            edges += 1

                        self.edgeservice.add_follower_edges(user_id, resp_follower_ids)
                        cursor = follower['next_cursor']

                self.scrapeservice.finished(user_id, 'follow')

                if i % 20 == 0:
                    logging.info('Recorded %d edges.', edges)
                    edges = 0

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))

