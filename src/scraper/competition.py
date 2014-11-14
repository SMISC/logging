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
        self.threads = []

    def main(self):
        if not self.lockservice.acquire():
            return

        if self.myscrapeservice.length() == 0:
            logging.info('Queue %s is empty. Beginning anew...', type(self))
            competition_users = self.userservice.get_competition_users()

            for user_id in competition_users:
                self.myscrapeservice.enqueue(user_id)

        self._run_user_queue()

        queue_length = self.myscrapeservice.length()
        logging.info('%d users remaining for %s', queue_length, type(self))

        for thread in self.threads:
            thread.start()
        
        for thread in self.threads:
            thread.join()
