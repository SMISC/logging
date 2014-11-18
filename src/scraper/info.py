import signal
import threading
import logging

from .competition import CompetitionScraper
from .infoworker import InfoScraperWorker

class InfoScraper(CompetitionScraper):
    def __init__(self, rlapis, userservices, myuserservice, lockservice, scrapeservices):
        CompetitionScraper.__init__(self, myuserservice, lockservice, scrapeservices)
        self.rlapis = rlapis
        self.userservices = userservices

    def _generate_queue(self, users):
        for user_id in users:
            self.myscrapeservice.enqueue(user_id)

    def _run_user_queue(self):
        logging.info('Info scraper started')

        n_threads = len(self.rlapis)

        for i in range(n_threads):
            thread = InfoScraperWorker(self.rlapis[i], self.userservices[i], self.scrapeservices[i])
            self.threads.append(thread)
