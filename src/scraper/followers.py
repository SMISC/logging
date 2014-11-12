import queue
import time
import signal
import threading
import logging

from .followerworker import FollowersScraperWorker

class FollowersScraper:
    LOCK_KEY = 'follower_scraper'

    def __init__(self, rlapis, edgeservices, userservice, lockservice):
        self.rlapis = rlapis
        self.edgeservices = edgeservices
        self.userservice = userservice
        self.lockservice = lockservice
        self.evt = threading.Event()
        self.threads = []

    def main(self):
        signal.signal(signal.SIGTERM, self.cleanup)
        acquired = self.lockservice.acquire(self.LOCK_KEY)

        if not acquired:
            time_started = self.lockservice.inspect(self.LOCK_KEY)
            logging.info('Follower scraper locked (since %.0f minutes ago). Quitting...', (time.time() - time_started) / 60)
            return

        logging.info('Follower scraper started')

        q = queue.Queue()

        for i in range(len(self.rlapis)):
            logging.debug('Starting follower worker')
            thread = FollowersScraperWorker(q, self.rlapis[i], self.edgeservices[i], self.evt)
            self.threads.append(thread)
            thread.start()

        page = 0
        pagesize = 1000
        users = []

        while page == 0 or len(users) is not 0:
            users = self.userservice.users_where('interesting=True', [], 'id asc', pagesize, page*pagesize)
            logging.info("Got %d users on page %d", len(users), page)
            page = page + 1

    def cleanup(self):
        logging.info('Got TERM signal, exiting gracefully...')
        self.evt.set()
        for thread in self.threads:
            thread.join()
