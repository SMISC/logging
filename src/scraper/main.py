import threading
import configparser
import datetime
import psycopg2
import redis
import sys

from TwitterAPI import TwitterAPI

# from common.scraper import ScrapeJob
from common.scraper import ScrapeService

from common.tweet import TweetService
from common.user import UserService

import time

def main(dbc, rds, logfile):
    last_tweet_id = 0
    
    current_scan_id = int(rds.get('current_scan'))

    tweetservice = TweetService(dbc.cursor())
    userservice = UserService(dbc.cursor())
    scrapeservice = ScrapeService(rds)
    scrapeservice.set_current_scan_id(current_scan_id)

    try:
        while True:
            recent_tweets = tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            
            user_ids = []
            for tweet in recent_tweets:
                user_ids.append(tweet['user_id'])
                last_tweet_id = max(last_tweet_id, tweet['tweet_id'])

            user_ids_set = set(user_ids)

            users_in_postgres = userservice.users_where('user_id in %s', [tuple(user_ids)])

            for user_id in users_in_postgres:
                user_ids_set.discard(user['user_id'])

            for user_id in user_ids_set:
                if not scrapeservice.is_user_queued(user_id):
                    new_users += 1
                    scrapeservice.enqueue(user_id)

            print("[scraper-main] backlog: %d\t\t%d pushed this cycle\t\t%d total processed" % (scrapeservice.length(), new_users, scrapeservice.total_processed()))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Caught interrupt signal. Exiting...", file=logfile)
        scrapeservice.erase()
    
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

    main(api, dbc, rds, logfile)
