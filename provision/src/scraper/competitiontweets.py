import time
import signal
import threading
import logging

from .competitiontweetsworker import CompetitionTweetsScraperWorker
from .competition import CompetitionScraper

class CompetitionTweetsScraper(CompetitionScraper):
    def __init__(self, rlapis, tweetservices, userservice, lockservice, scrapeservices, scanservice, stats):
        CompetitionScraper.__init__(self, userservice, lockservice, scrapeservices, scanservice)
        self.rlapis = rlapis
        self.tweetservices = tweetservices
        self.stats = stats

    def _generate_queue(self, users):
        for user in users:
            self.myscrapeservice.enqueue({
                "user_id": user["twitter_id"],
                "since_id": None
            })

    def _run_user_queue(self):
        n_threads = len(self.rlapis)

        for i in range(n_threads):
            thread = CompetitionTweetsScraperWorker(self.scrapeservices[i], self.rlapis[i], self.tweetservices[i], self.stats)
            self.threads.append(thread)
