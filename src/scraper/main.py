import threading
import configparser
import datetime
import psycopg2
import redis
import sys

from TwitterAPI import TwitterAPI

from common.filtr import FilterJob
from common.filtr import FilterService

from common.scraper import ScrapeJob
from common.scraper import ScrapeService

from common.tweet import TweetService
from common.user import UserService

import time

def main(dbc, rds, logfile):
    last_tweet_id = 0
    tweetservice = TweetService(dbc.cursor())
    userservice = UserService(dbc.cursor())

    while True:
        filter_passes = 0
        while filter_passes < 5:
            recent_tweets = tweetservice.get_recent_tweets(last_tweet_id)
            
            user_ids = []
            for tweet in recent_tweets:
                user_ids.append(tweet['user_id'])

            users_in_postgres = userservice.

                if tweet['user_id'] not in in_progress_user_ids and tweet['user_id'] not in queued_user_ids:
                    new_users += 1
                    rds.push(tweet['user_id'])

            last_tweet_id = max(last_tweet_id, tweet['tweet_id'])

        print("[scraper-main] backlog: %d\t\tin progress: %d\t\t%d pushed this cycle" % (backlog, len(), new_users))
            
    def get_recent_tweets(self, min_tweet_id, batch_size = 100):
        time.sleep(1)

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

    main(api, dbc, rds, logfile)
