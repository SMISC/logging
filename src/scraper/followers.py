import queue
import time
import signal
import threading
import logging

from .competition import CompetitionScraper
from .followerworker import FollowersScraperWorker

class FollowersScraper(CompetitionScraper):
    LOCK_KEY = 'follower_scraper'

    def __init__(self, rlapis, edgeservices, userservice, lockservice):
        CompetitionScraper.__init__(self, userservice, lockservice)
        self.rlapis = rlapis
        self.edgeservices = edgeservices
        self.evt = threading.Event()
        self.threads = []

    def _run_user_queue(self, q):
        logging.info('Follower scraper started')

        for i in range(len(self.rlapis)):
            thread = FollowersScraperWorker(q, self.rlapis[i], self.edgeservices[i], self.evt)
            self.threads.append(thread)
            thread.start()
