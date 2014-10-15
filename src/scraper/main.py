import threading
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
    def __init__(self, dbc, rds, credentials):
        self.dbc = dbc
        self.rds = rds
        self.credentials = credentials
        self.jobs = []
        self.wakeup = threading.Event()

    def main(self):
        last_tweet_id = 0
        
        current_scan_id = int(self.rds.get('current_scan'))

        print('[scraper-main] Current scan: %d' % (current_scan_id))

        tweetservice = TweetService(self.dbc.cursor())
        userservice = UserService(self.dbc.cursor())
        scrapeservice = ScrapeService(self.rds, current_scan_id)

        print('[scraper-main] Initializing follower scrapers...')
        sys.stdout.flush()

        for (key, secret) in self.credentials[:-1]: # save one for user info scraper
            print('[scraper-main] Creating follower thread')
            sys.stdout.flush()
            edgeservice = EdgeService(self.dbc.cursor())
            edgeservice.set_current_scan_id(current_scan_id)
            api = TwitterAPI(key, secret, auth_type='oAuth2')
            rlapi = RateLimitedTwitterAPI(api, self.wakeup)
            sys.stdout.flush()
            rlapi.update()
            followjob = ScrapeFollowersJob(rlapi, edgeservice, scrapeservice, self.wakeup)
            self.jobs.append(followjob)
        
        print('[scraper-main] Creating info thread')
        (infokey, infosecret) = self.credentials[-1]
        infoapi = TwitterAPI(infokey, infosecret, auth_type='oAuth2')
        rlinfoapi = RateLimitedTwitterAPI(infoapi, self.wakeup)
        sys.stdout.flush()
        rlinfoapi.update()
        infojob = ScrapeInfoJob(rlinfoapi, userservice, scrapeservice, self.wakeup)
        self.jobs.append(infojob)

        print('[scraper-main] Starting jobs...')

        for job in self.jobs:
            pass#job.start()

        print('[scraper-main] Polling for tweets for user ids starting at %d' % (last_tweet_id))
        self.stdout.flush()
        
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        while True:
            recent_tweets = tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            print('[scraper-main] Grabbed %d recent tweets' % (len(recent_tweets)))
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
                    if not scrapeservice.is_user_queued(user_id):
                        new_users += 1
                        scrapeservice.enqueue(user_id)

            print('[scraper-main] backlog [%d info] [%d follow]\t\t%d pushed this cycle\t\t%d total processed' % (scrapeservice.length('info'), scrapeservice.length('follow'), new_users, scrapeservice.total_processed()))
            time.sleep(10)
        
        self.dbc.close()
    def cleanup(self):
        print('Caught signal. Exiting gracefully...')
        self.dbc.close()
        self.wakeup.set()
        self.scrapeservice.erase(['follow', 'info'])
        for job in self.jobs:
            job.join()

if __name__ == "__main__":
    print("Pacsocial Twitter Scraper")

    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    print("Pacsocial Twitter Scraper started at %s" % (datetime.datetime.now().strftime("%b %d %H:%M:%S")))

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    creds = []
    keys = config['twitter-worker']['keys'].split("\n")
    secrets = config['twitter-worker']['secrets'].split("\n")

    if len(keys) != len(secrets):
        print("Error: Mismatch in number of keys (%d) and secrets (%d)" % (len(keys), len(secrets)))
        sys.exit(1)

    for i in range(len(keys)):
        creds.append((keys[i], secrets[i]))

    scraper = ScraperMain(dbc, rds, creds)
    scraper.main()
