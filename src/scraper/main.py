import threading
import logging
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

class ScraperMain:
    def __init__(self, log, dbc, rds, credentials):
        self.dbc = dbc
        self.rds = rds
        self.credentials = credentials
        self.jobs = []
        self.log = log
        self.scrapeservice = None
        self.wakeup = threading.Event()

    def main(self):
        last_tweet_id = 0
        
        current_scan_id = int(self.rds.get('current_scan'))

        self.log.debug('Current scan: %d' % (current_scan_id))

        tweetservice = TweetService(self.dbc.cursor())
        userservice = UserService(self.dbc.cursor())
        self.scrapeservice = ScrapeService(self.rds, current_scan_id)

        self.log.debug('Initializing follower scrapers...')

        for (key, secret) in self.credentials[:-1]: # save one for user info scraper
            self.log.debug('[scraper-main] Creating follower thread')
            edgeservice = EdgeService(self.dbc.cursor())
            edgeservice.set_current_scan_id(current_scan_id)
            api = TwitterAPI(key, secret, auth_type='oAuth2')
            rlapi = RateLimitedTwitterAPI(self.log.getChild('ratelimit'), api, self.wakeup)
            rlapi.update()
            followjob = ScrapeFollowersJob(self.log.getChild('followers'), rlapi, edgeservice, self.scrapeservice, self.wakeup)
            self.jobs.append(followjob)
        
        self.log.debug('Creating info thread')
        (infokey, infosecret) = self.credentials[-1]
        infoapi = TwitterAPI(infokey, infosecret, auth_type='oAuth2')
        rlinfoapi = RateLimitedTwitterAPI(self.log.getChild('ratelimit'), infoapi, self.wakeup)
        rlinfoapi.update()
        infojob = ScrapeInfoJob(self.log.getChild('info'), rlinfoapi, userservice, self.scrapeservice, self.wakeup)
        self.jobs.append(infojob)

        self.log.debug('Starting jobs...')

        for job in self.jobs:
            job.start()

        self.log.info('Polling for tweets for user ids starting at %d' % (last_tweet_id))
        sys.stdout.flush()
        
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        while True:
            self.log.debug('There are %d active workers.' % (threading.active_count()))
            recent_tweets = tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            self.log.info('Grabbed %d recent tweets since %d' % (len(recent_tweets)))
            sys.stdout.flush()
            
            user_ids = []
            for tweet in recent_tweets:
                user_ids.append(str(tweet['user_id'])) # postgresql wants string-keys
                last_tweet_id = max(last_tweet_id, tweet['tweet_id'])

            user_ids_set = set(user_ids)

            new_users = 0

            if len(user_ids):
                users_in_postgres = userservice.users_where('user_id in %s', [tuple(user_ids)])

                for user_id in users_in_postgres:
                    user_ids_set.discard(user['user_id'])

                for user_id in user_ids_set:
                    if not self.scrapeservice.is_user_queued(user_id):
                        new_users += 1
                        self.scrapeservice.enqueue(user_id)

            self.log.info('backlog [%d info] [%d follow]\t\t%d pushed this cycle\t\t%d total processed' % (self.scrapeservice.length('info'), self.scrapeservice.length('follow'), new_users, self.scrapeservice.total_processed()))
            time.sleep(10)
        
        self.dbc.close()
    def cleanup(self):
        self.log.info('Caught signal. Exiting gracefully...')
        self.dbc.close()
        self.wakeup.set()
        self.scrapeservice.erase(['follow', 'info'])
        for job in self.jobs:
            job.join()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    log = logging.getLogger('smisc.manager')
    handler = logging.FileHandler(config['bot']['log'])
    formatter = logging.Formatter('%(asctime):%(name)s:%(levelname): %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('SMISC Manager started')

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    creds = []
    keys = config['twitter-worker']['keys'].split("\n")
    secrets = config['twitter-worker']['secrets'].split("\n")

    if len(keys) != len(secrets):
        mlog.error('Error: Mismatch in number of keys (%d) and secrets (%d)' % (len(keys), len(secrets)))
        sys.exit(1)

    for i in range(len(keys)):
        creds.append((keys[i], secrets[i]))

    scraper = ScraperMain(log, dbc, rds, creds)
    try:
        scraper.main()
    except Exception as err:
        log.exception('Caught error: %s' % (str(err)))
        scraper.cleanup()
