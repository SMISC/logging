import threading
import configparser
import datetime
import psycopg2
import redis
import sys

from TwitterAPI import TwitterAPI

from common.scraper import ScrapeJob
from common.scraper import ScrapeService

from common.tweet import TweetService
from common.user import UserService
from common.edge import EdgeService
from common.ratelimit import RateLimitedTwitterAPI

import time

def main(dbc, rds, logfile, credentials):
    last_tweet_id = 0
    
    current_scan_id = int(rds.get('current_scan'))

    tweetservice = TweetService(dbc.cursor())
    userservice = UserService(dbc.cursor())
    scrapeservice = ScrapeService(rds)
    scrapeservice.set_current_scan_id(current_scan_id)

    followjobs = []

    print("[scraper-main] Initializing follower scrapers...", file=logfile)
    logfile.flush()

    for (key, secret) in credentials:
        edgeservice = EdgeService(dbc.cursor())
        edgeservice.set_current_scan_id(current_scan_id)
        api = TwitterAPI(key, secret, auth_type='oAuth2')
        rlapi = RateLimitedTwitterAPI(api)
        rlapi.update()
        followjob = ScrapeJob(rlapi, edgeservice, scrapeservice, logfile)
        followjobs.append(followjob)

    for job in followjobs:
        job.start()

    print("[scraper-main] Polling for tweets for user ids", file=logfile)
    logfile.flush()

    try:
        while True:
            recent_tweets = tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            
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

            print("[scraper-main] backlog: %d\t\t%d pushed this cycle\t\t%d total processed" % (scrapeservice.length(), new_users, scrapeservice.total_processed()), file=logfile)
            time.sleep(10)
            logfile.flush()
    except KeyboardInterrupt:
        print("Caught interrupt signal. Exiting...", file=logfile)
        scrapeservice.erase()
        for job in followjobs:
            job.abort()
    
    dbc.close()

if __name__ == "__main__":
    print("Pacsocial Twitter Scraper")

    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    logfile = open(config['bot']['log'], 'a+')
    sys.stdout = logfile
    sys.stderr = logfile

    print("Pacsocial Twitter Scraper started at %s" % (datetime.datetime.now().strftime("%b %d %H:%M:%S")), file=logfile)

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

    main(dbc, rds, logfile, creds)
