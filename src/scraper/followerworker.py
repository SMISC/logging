import time
import threading
import logging
import queue

class FollowersScraperWorker(threading.Thread):
    def __init__(self, q, rlapi, edgeservice, evt):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.edgeservice = edgeservice
        self.q = q
        self.evt = evt

    def run(self):
        try:
            edges = 0
            i = 0
            while not self.evt.is_set():
                time.sleep(1)
                try:
                    user_id = self.q.get(block=False)
                except queue.Empty:
                    continue

                cursor = -1
                pagen = 0
                while cursor <= 0:
                    logging.info('Getting %dth page of followers for %d', pagen, user_id)
                    pagen += 1
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

                logging.debug('Recorded %d edges.', edges)

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))

