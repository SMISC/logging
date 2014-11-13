from ratelimit import ProtectedException

import time
import threading
import logging
import queue

class FollowersScraperWorker(threading.Thread):
    def __init__(self, scrapeservice, rlapi, edgeservice):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.edgeservice = edgeservice
        self.scrapeservice = scrapeservice

    def run(self):
        try:
            user_id = self.scrapeservice.dequeue()
            if user_id is None:
                return

            cursor = -1
            pagen = 0
            while cursor != 0:
                logging.info('Getting %dth page of followers for %s', pagen, user_id)
                pagen += 1

                try:
                    resp = self.rlapi.request('followers/ids', {'user_id': user_id, 'count': 5000, 'cursor': cursor})
                except ProtectedException as e:
                    logging.info('%d is protected.', user_id)
                    break

                resp_follower_ids = []

                for fid in resp['ids']:
                    resp_follower_ids.append(str(fid))

                self.edgeservice.add_follower_edges(user_id, resp_follower_ids)
                cursor = resp['next_cursor']
                time.sleep(5)

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))

