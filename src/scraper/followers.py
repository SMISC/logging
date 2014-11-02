import signal
import threading
import logging

from .followerworker import FollowersScraperWorker

class InfoScraper:
    def __init__(self, rlapis, userservice, scrapeservice):
        self.rlapis = rlapis
        self.scrapeservice = scrapeservice
        self.userservice = userservice
        self.evt = threading.Event()
        self.threads = []
    def main(self):
        signal.signal(signal.SIGTERM, self.cleanup)
        for rlapi in self.rlapis:
            logging.debug('Starting follower worker')
            thread = FollowerScraperWorker(rlapi, self.edgeservice, self.scrapeservice, self.evt)
            self.threads.append(thread)
            thread.start()
    def cleanup(self):
        logging.info('Got TERM signal, exiting gracefully...')
        self.evt.set()
        for thread in self.threads:
            thread.join()
