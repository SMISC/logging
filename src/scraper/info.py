import signal
import threading
import logging

from .infoworker import InfoScraperWorker

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
            logging.debug('Starting infoscraper worker')
            thread = InfoScraperWorker(self.rlapis[i], self.userservices[i], self.scrapeservices[i], self.evt)
            self.threads.append(thread)
            thread.start()
    def cleanup(self):
        logging.info('Got TERM signal, exiting gracefully...')
        self.evt.set()
        for thread in self.threads:
            thread.join()
