import queue
import time
import signal
import threading
import logging

from .competition import CompetitionScraper
from .followerworker import FollowersScraperWorker

class FollowersScraper(CompetitionScraper):
    def __init__(self, rlapis, edgeservices, userservice, lockservice, scrapeservices, scanservice):
        CompetitionScraper.__init__(self, userservice, lockservice, scrapeservices, scanservice)
        self.rlapis = rlapis
        self.edgeservices = edgeservices

    def _generate_queue(self, users):
        pass

    def _run_user_queue(self):
        pass

class BotFollowersScraper(FollowersScraper):
    def __init__(self, rlapis, edgeservices, userservice, lockservice, scrapeservices, scanservice, botservices):
        FollowersScraper.__init__(self, rlapis, edgeservices, userservice, lockservice, scrapeservices, scanservice)
        self.botservices = botservices

    def _run_user_queue(self):
        n_threads = len(self.rlapis)

        for i in range(n_threads):
            thread = FollowersScraperWorker(self.scrapeservices[i], self.rlapis[i], self.edgeservices[i], self.botservices[i])
            self.threads.append(thread)

    def _generate_queue(self, users):
        for user in users:
            self.myscrapeservice.enqueue({
                "user_id": user["twitter_id"],
                "cursor": -1,
                "bot": True
            })

    def get_competition_users(self):
        return self.botservices[0].get_bots()

class WideFollowersScraper(FollowersScraper):
    def _run_user_queue(self):
        n_threads = len(self.rlapis)

        for i in range(n_threads):
            thread = FollowersScraperWorker(self.scrapeservices[i], self.rlapis[i], self.edgeservices[i])
            self.threads.append(thread)

    def _generate_queue(self, users):
        for user in users:
            self.myscrapeservice.enqueue({
                "user_id": user["twitter_id"],
                "cursor": -1,
                "bot": False
            })
