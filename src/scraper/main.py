import threading
import logging
import logging.handlers
import configparser
import datetime
import psycopg2
import redis
import sys
import signal

from TwitterAPI import TwitterAPI

from common.scraper import ScrapeFollowersJob
from common.scraper import ScrapeInfoJob
from common.scraper import ScrapeService

from common.tweet import TweetService
from common.user import UserService
from common.edge import EdgeService
from common.ratelimit import RateLimitedTwitterAPI

import time

THREADS_FOLLOWERS = 13

class ScraperMain:
    def __init__(self, dbc, rds, credentials):
        self.dbc = dbc
        self.rds = rds
        self.credentials = credentials
        self.jobs = []
        self.scrapeservice = None
        self.wakeup = threading.Event()

    def main(self):
        last_tweet_id = 0
        
        current_scan_id = int(self.rds.get('current_scan'))

        logging.info('Current scan: %d', current_scan_id)

        tweetservice = TweetService(self.dbc.cursor())
        userservice = UserService(self.dbc.cursor())
        self.scrapeservice = ScrapeService(self.rds, current_scan_id)

        logging.debug('Initializing follower scrapers...')

        followers_credentials = self.credentials[:THREADS_FOLLOWERS]
        info_credentials = self.credentials[THREADS_FOLLOWERS:]

        for (key, secret) in followers_credentials:
            logging.info('Creating follower thread')
            edgeservice = EdgeService(self.dbc.cursor())
            edgeservice.set_current_scan_id(current_scan_id)
            api = TwitterAPI(key, secret, auth_type='oAuth2')
            rlapi = RateLimitedTwitterAPI(api, self.wakeup)
            rlapi.update()
            followjob = ScrapeFollowersJob(rlapi, edgeservice, self.scrapeservice, self.wakeup)
            self.jobs.append(followjob)
        
        for (key, secret) in info_credentials:
            logging.info('Creating info thread')
            infoapi = TwitterAPI(key, secret, auth_type='oAuth2')
            rlinfoapi = RateLimitedTwitterAPI(infoapi, self.wakeup)
            rlinfoapi.update()
            infojob = ScrapeInfoJob(rlinfoapi, userservice, self.scrapeservice, self.wakeup)
            self.jobs.append(infojob)

        logging.debug('Starting jobs...')

        for job in self.jobs:
            job.start()

        logging.info('Polling for tweets for user ids starting at %d', last_tweet_id)
        
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        while not self.wakeup.is_set():
            logging.debug('There are %d active workers', threading.active_count())
            recent_tweets = tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            
            user_ids = []
            for tweet in recent_tweets:
                user_ids.append(tweet['user_id'])
                last_tweet_id = max(last_tweet_id, tweet['tweet_id'])

            user_ids_set = set(user_ids)

            new_users = 0

            if len(user_ids):
                users_in_postgres = userservice.users_where('user_id in %s', [tuple(user_ids)])

                for user in users_in_postgres:
                    user_ids_set.discard(user['user_id'])

                for user_id in user_ids_set:
                    if not self.scrapeservice.is_user_queued(user_id):
                        new_users += 1
                        self.scrapeservice.enqueue('follow', user_id)

            logging.info('scrape backlog [%d info] [%d follow]\t\t%d pushed this cycle\t\t%d total processed', self.scrapeservice.length('info'), self.scrapeservice.length('follow'), new_users, self.scrapeservice.total_processed())
            self.wakeup.wait(10)
        
        self.dbc.close()

    def cleanup(self):
        logging.info('Caught signal. Exiting gracefully...')
        self.dbc.close()
        self.wakeup.set()
        self.scrapeservice.erase(['follow', 'info'])
        for job in self.jobs:
            job.join()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    log = logging.getLogger(None)
    handler = logging.handlers.RotatingFileHandler(config['bot']['log'], maxBytes=1024*1024*10, backupCount=5)
    formatter = logging.Formatter('{asctime}\t{name}\t{levelname}\t\t{message}', style='{')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    logging.getLogger('requests').setLevel(logging.ERROR)

    log.info('SMISC Manager started')

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    creds = []
    keys = config['twitter-worker']['keys'].split("\n")
    secrets = config['twitter-worker']['secrets'].split("\n")

    if len(keys) != len(secrets):
        logging.exception('Error: Mismatch in number of keys (%d) and secrets (%d)' % (len(keys), len(secrets)))
        sys.exit(1)

    for i in range(len(keys)):
        creds.append((keys[i], secrets[i]))

    scraper = ScraperMain(dbc, rds, creds)
    try:
        scraper.main()
    except Exception as err:
        logging.exception('Caught error: %s' % (str(err)))
        scraper.cleanup()
