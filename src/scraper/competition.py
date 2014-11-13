import queue
import time
import signal
import threading
import logging

class CompetitionScraper:
    def __init__(self, userservice, lockservice, scrapeservices):
        self.userservice = userservice
        self.lockservice = lockservice
        self.scrapeservices = scrapeservices[1:]
        self.myscrapeservice = scrapeservices[0]

    def main(self):
        if not self.lockservice.acquire(self.LOCK_KEY):
            return

        if self.myscrapeservice.length() == 0:
            competition_users = self.userservice.get_competition_users()

            for user_id in competition_users:
                self.myscrapeservice.enqueue(user_id)

        self._run_user_queue()

        queue_length = self.myscrapeservice.length()
        logging.info('%d users remaining', queue_length)

        self.lockservice.release(self.LOCK_KEY)
