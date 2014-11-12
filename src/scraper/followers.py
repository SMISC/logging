import queue
import time
import signal
import threading
import logging

from .followerworker import FollowersScraperWorker

class FollowersScraper:
    LOCK_KEY = 'follower_scraper'

    def __init__(self, rlapis, edgeservices, db, lockservice):
        self.rlapis = rlapis
        self.edgeservices = edgeservices
        self.db = db
        self.lockservice = lockservice
        self.evt = threading.Event()
        self.threads = []

    def main(self):
        if not self.lockservice.acquire(self.LOCK_KEY):
            return

        logging.info('Follower scraper started')

        signal.signal(signal.SIGTERM, self.sigterm)
        q = queue.Queue()

        for i in range(len(self.rlapis)):
            logging.debug('Starting follower worker')
            thread = FollowersScraperWorker(q, self.rlapis[i], self.edgeservices[i], self.evt)
            self.threads.append(thread)
            thread.start()

        page = 0
        pagesize = 1000
        users = 0

        while page is 0 or users is not 0:
            self.db.execute('select distinct on (user_id) id, user_id from tuser where interesting=True order by user_id, id asc limit %d offset %d' % (pagesize, pagesize*page))

            users = 0

            try:
                users_results = self.db.fetchall()
            except psycopg2.ProgrammingError:
                users_results = []

            if users_results is None:
                users_results = []

            for user_result in users_results:
                user_id = user_result[1]
                users += 1
                q.put(str(user_id))

            page = page + 1

        while not q.empty():
            logging.info('%d users remaining', q.qsize())
            time.sleep(10)

        logging.info('Done!')
        self.cleanup()

    def sigterm(self):
        logging.info('Got TERM signal, exiting gracefully...')
        self.cleanup()

    def cleanup(self):
        logging.info('Cleaning up...')
        self.lockservice.release(self.LOCK_KEY)
        self.evt.set()
