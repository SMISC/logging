import time
import signal
import threading
import logging

from .competitiontweetsworker import CompetitionTweetsScraperWorker
from .competition import CompetitionScraper

class CompetitionTweetsScraper(CompetitionScraper):
    LOCK_KEY = 'competition_tweets_scraper'
    def __init__(self, rlapis, tweetservices, userservice, lockservice, scrapeservices):
        CompetitionScraper.__init__(self, userservice, lockservice, scrapeservices)
        self.rlapis = rlapis
        self.tweetservices = tweetservices

    def _generate_queue(self, users):
        for user_id in users:
            self.myscrapeservice.enqueue({
                "user_id": user_id,
                "since_id": None
            })

    def _run_user_queue(self):
        logging.info('Competition tweet scraper started')

        n_threads = len(self.rlapis)

        for i in range(n_threads):
            thread = CompetitionTweetsScraperWorker(self.scrapeservices[i], self.rlapis[i], self.tweetservices[i])
            self.threads.append(thread)
