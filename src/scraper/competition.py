import queue
import time
import signal
import threading
import logging

class CompetitionScraper:
    def __init__(self, userservice, lockservice, scrapeservices, scanservice):
        self.userservice = userservice
        self.lockservice = lockservice
        self.scrapeservices = scrapeservices[1:]
        self.myscrapeservice = scrapeservices[0]
        self.scanservice = scanservice
        self.threads = []

    def get_competition_users(self):
        return self.userservice.get_competition_users()

    def main(self):
        if not self.lockservice.acquire():
            return

        if self.myscrapeservice.length() == 0:
            logging.info('Queue %s is empty. Beginning anew...', type(self))
            self.scanservice.begin_anew()
            competition_users = self.get_competition_users()

            self._generate_queue(competition_users)

        self._run_user_queue()

        queue_length = self.myscrapeservice.length()
        logging.info('%d users remaining for %s', queue_length, type(self))

        for thread in self.threads:
            thread.start()
        
        for thread in self.threads:
            thread.join()

        queue_length = self.myscrapeservice.length()
        logging.info('%d users remaining for %s', queue_length, type(self))
