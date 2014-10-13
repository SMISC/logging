import sys
import os
import queue
import redis
import psycopg2
import time
import configparser
import datetime

from TwitterAPI import TwitterAPI

from manager.manager.scan import Scan
from manager.manager.scan import ScanService

from common.tweet import TweetService
from common.ratelimit import RateLimitedTwitterAPI

def main(api, dbc, rds, logfile):
    print("[manager-main] Inspecting rate limit status...", file=logfile)

    rlapi = RateLimitedTwitterAPI(api)
    rlapi.update()

    scanservice = ScanService(dbc.cursor())
    start_time = int(time.time())
    max_breadth = 2
    scan = scanservice.new_scan(start_time, max_breadth)
    rds.set('current_scan', scan.get_id())
    print("[manager-main] Starting scan %d" % (scan.get_id()), file=logfile)
    db = dbc.cursor()
    tweetservice = TweetService(dbc.cursor())

    try:
        query = '#vaxtruth OR #vaccinedebate OR #hearthiswell OR #cdcfraud OR #vaccinescauseautism OR #cdcfraudexposed OR #cdccoverup OR #cdcwhistleblower OR #parentsdothework OR #saynotovaccines OR #vaccineeducated'
        max_id = None
        since_id = tweetservice.get_latest_tweet_id()

        since_dt = 'the beginning of time'
        max_dt = ''

        while True:
            if max_id is None and since_id is None:
                # first query ever
                print("[manager-main] Seeking any tweets we can get.", file=logfile)
                results = rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100})
            elif max_id is not None: # seeking old
                print("[manager-main] Seeking old tweets before %s (%d)" % (max_dt, max_id), file=logfile)
                results = rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100, 'max_id': max_id})
            else: # seeking new
                print("[manager-main] Seeking new tweets since %s (%d)" % (since_dt, since_id), file=logfile)
                results = rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100, 'since_id': since_id})

            entities = []
            max_tweet_id = None
            min_tweet_id = None
            min_dt = ''
            max_dt = ''

            for status in results.get_iterator():
                tweet_id = int(status["id"])

                tweetservice.queue_tweet(status)

                if min_tweet_id is None:
                    min_tweet_id = tweet_id
                    min_dt = status["created_at"]
                else:
                    min_tweet_id = min(min_tweet_id, tweet_id)
                    min_dt = status["created_at"]

                if max_tweet_id is None:
                    max_tweet_id = tweet_id
                    max_dt = status["created_at"]
                else:
                    max_tweet_id = max(max_tweet_id, tweet_id)
                    max_dt = status["created_at"]

            n_tweets = tweetservice.get_number_of_queued()

            tweetservice.commit()

            print("[manager-main] Found %d tweets." % (n_tweets), file=logfile)

            if n_tweets < 100:
                # we got less than expected. switch to polling for new tweets.
                since_id = tweetservice.get_latest_tweet_id()
                if max_id is not None:
                    # were paging. no clue what the date was
                    since_dt = '(?)'
                else:
                    since_dt = max_dt

                max_dt = ''
                max_id = None
                time.sleep(20)
            else:
                # we got 100. start paging.
                since_id = None
                since_dt = ''
                max_id = min_tweet_id - 1
                max_dt = min_dt

            logfile.flush()
            time.sleep(1)
                
    except KeyboardInterrupt:
        print("[manager-main] Caught interrupt signal. Exiting...", file=logfile)
    
    scanservice.done(int(time.time()))

    dbc.close()

if __name__ == "__main__":
    print("Pacsocial Twitter Scanner")

    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    logfile = open(config['bot']['log'], 'a+')
    sys.stdout = logfile
    sys.stderr = logfile

    print("Pacsocial Twitter Scanner started at %s" % (datetime.datetime.now().strftime("%b %d %H:%M:%S")), file=logfile)

    api = TwitterAPI(config['twitter-manager']['key'], config['twitter-manager']['secret'], auth_type='oAuth2')

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    main(api, dbc, rds, logfile)
