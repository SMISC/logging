import queue
import time
import signal
import threading
import logging

class CompetitionScraper:
    def __init__(self, userservice, lockservice):
        self.userservice = userservice
        self.lockservice = lockservice

    def main(self):
        if not self.lockservice.acquire(self.LOCK_KEY):
            return

        signal.signal(signal.SIGTERM, self.sigterm)
        q = queue.Queue()

        competition_users = self.userservice.get_competition_users()

        for user_id in competition_users:
            q.put(user_id)

        self._run_user_queue(q)

        while not q.empty():
            logging.info('%d users remaining', q.qsize())
            time.sleep(10)

        logging.info('Done!')
        self.cleanup()

    def sigterm(self, d, u):
        logging.info('Got TERM signal, exiting gracefully...')
        self.cleanup()

    def cleanup(self):
        logging.info('Cleaning up...')
        self.lockservice.release(self.LOCK_KEY)
        self.evt.set()
