import signal
import threading
import logging

from .followerworker import FollowersScraperWorker

class InfoScraper:
    def __init__(self, rlapis, userservices, scrapeservices):
        self.rlapis = rlapis
        self.scrapeservices = scrapeservices
        self.userservices = userservices
        self.evt = threading.Event()
        self.threads = []
    def main(self):
        signal.signal(signal.SIGTERM, self.cleanup)
        for i in range(len(self.rlapis)):
            logging.debug('Starting follower worker')
            thread = FollowerScraperWorker(rlapis[i], self.edgeservices[i], self.scrapeservices[i], self.evt)
            self.threads.append(thread)
            thread.start()
    def cleanup(self):
        logging.info('Got TERM signal, exiting gracefully...')
        self.evt.set()
        for thread in self.threads:
            thread.join()
