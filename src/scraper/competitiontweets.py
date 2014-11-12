import time
import signal
import threading
import logging

from .competitiontweetsworker import CompetitionTweetsScraperWorker
from .competition import CompetitionScraper

class CompetitionTweetsScraper(CompetitionScraper):
    LOCK_KEY = 'competition_tweets_scraper'

    def __init__(self, rlapis, tweetservices, userservice, lockservice):
        CompetitionScraper.__init__(self, userservice, lockservice)
        self.rlapis = rlapis
        self.tweetservices = tweetservices
        self.evt = threading.Event()
        self.threads = []

    def _run_user_queue(self, q):
        logging.info('Competition tweet scraper started')

        for i in range(len(self.rlapis)):
            thread = CompetitionTweetsScraperWorker(q, self.rlapis[i], self.tweetservices[i], self.evt)
            self.threads.append(thread)
            thread.start()
