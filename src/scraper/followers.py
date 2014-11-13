import queue
import time
import signal
import threading
import logging

from .competition import CompetitionScraper
from .followerworker import FollowersScraperWorker

class FollowersScraper(CompetitionScraper):
    LOCK_KEY = 'follower_scraper'

    def __init__(self, rlapis, edgeservices, userservice, lockservice, scrapeservices):
        CompetitionScraper.__init__(self, userservice, lockservice, scrapeservices)
        self.rlapis = rlapis
        self.edgeservices = edgeservices
        self.threads = []

    def _run_user_queue(self):
        logging.info('Follower scraper started')

        for i in range(len(self.rlapis)):
            thread = FollowersScraperWorker(self.scrapeservices[i], self.rlapis[i], self.edgeservices[i])
            self.threads.append(thread)
            thread.start()
