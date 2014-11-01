import threading
import logging

from .infoworker import InfoScraperWorker

from util import twittertime as twittertime

class InfoScraper:
    def __init__(self, rlapis, userservice, scrapeservice):
        self.rlapis = rlapis
        self.scrapeservice = scrapeservice
        self.userservice = userservice
        self.evt = threading.Event()
    def main(self):
        threads = []
        for rlapi in self.rlapis:
            logging.debug('Starting infoscraper worker')
            thread = InfoScraperWorker(rlapi, self.scrapeservice, self.userservice, self.evt)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
