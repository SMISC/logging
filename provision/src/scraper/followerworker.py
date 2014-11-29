from ratelimit import ProtectedException
from ratelimit import OverLimits
from ratelimit import NotFound

import time
import threading
import logging
import queue

logger = logging.getLogger(__name__)

class FollowersScraperWorker(threading.Thread):
    def __init__(self, scrapeservice, rlapi, edgeservice):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.edgeservice = edgeservice
        self.scrapeservice = scrapeservice

    def run(self):
        try:
            job = self.scrapeservice.dequeue()
            if job is None:
                return

            (user_id, cursor) = (job["user_id"], job["cursor"])

            logger.debug('Getting followers for %s with cursor %d', user_id, cursor)

            try:
                resp = self.rlapi.request('followers/ids', {'user_id': user_id, 'count': 5000, 'cursor': cursor})
            except ProtectedException as e:
                logger.info('%d is protected.', user_id)
                return
            except NotFound:
                logger.info('Skipping user %d not found', user_id)
            except OverLimits:
                logger.info('Requeueing because over limits')
                self.scrapeservice.enqueue({
                    "user_id": user_id,
                    "cursor": cursor
                })
                return

            resp_follower_ids = []

            for fid in resp['ids']:
                resp_follower_ids.append(str(fid))

            self.edgeservice.add_follower_edges(user_id, resp_follower_ids)
            next_cursor = resp['next_cursor']

            if next_cursor != 0:
                self.scrapeservice.enqueue({
                    "user_id": user_id,
                    "cursor": next_cursor
                })

        except Exception as err:
            logger.exception('Caught error: %s' % (str(err)))
