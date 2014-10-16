import sys
import os
import queue
import redis
import psycopg2
import time
import configparser
import datetime
import threading
import logging

from TwitterAPI import TwitterAPI

from manager.manager.scan import Scan
from manager.manager.scan import ScanService

from common.tweet import TweetService
from common.ratelimit import RateLimitedTwitterAPI

class ManagerMain:
    def __init__(self, log, api, dbc, rds):
        self.api = api
        self.dbc = dbc
        self.rds = rds
        self.log = log
        self.wait = threading.Event()

    def main(self):
        self.log.debug('Inspecting rate limit status...')

        rlapi = RateLimitedTwitterAPI(self.log.getChild('ratelimit'), self.api, self.wait)
        rlapi.update()

        scanservice = ScanService(self.dbc.cursor())
        start_time = int(time.time())
        max_breadth = 2
        scan = scanservice.new_scan(start_time, max_breadth)
        self.rds.set('current_scan', scan.get_id())

        self.log.info('Starting scan %d' % (scan.get_id()))
        db = self.dbc.cursor()
        tweetservice = TweetService(self.dbc.cursor())

        while not self.wait.is_set():
            query = '#vaxtruth OR #vaccinedebate OR #hearthiswell OR #cdcfraud OR #vaccinescauseautism OR #cdcfraudexposed OR #cdccoverup OR #cdcwhistleblower OR #parentsdothework OR #saynotovaccines OR #vaccineeducated'
            max_id = None
            since_id = tweetservice.get_latest_tweet_id()

            since_dt = 'the beginning of time'
            max_dt = ''

            while not self.wait.is_set():
                if max_id is None and since_id is None:
                    # first query ever
                    self.log.info('Seeking any tweets we can get.')
                    results = rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100})
                elif max_id is not None: # seeking old
                    self.log.info('Seeking old tweets before %s (%d)' % (max_dt, max_id))
                    results = rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100, 'max_id': max_id})
                else: # seeking new
                    self.log.info('Seeking new tweets since %s (%d)' % (since_dt, since_id))
                    results = rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100, 'since_id': since_id})

                entities = []
                max_tweet_id = None
                min_tweet_id = None
                min_dt = ''
                max_dt = ''

                for status in results.get_iterator():
                    tweet_id = int(status['id'])

                    tweetservice.queue_tweet(status)

                    if min_tweet_id is None:
                        min_tweet_id = tweet_id
                        min_dt = status['created_at']
                    else:
                        min_tweet_id = min(min_tweet_id, tweet_id)
                        min_dt = status['created_at']

                    if max_tweet_id is None:
                        max_tweet_id = tweet_id
                        max_dt = status['created_at']
                    else:
                        max_tweet_id = max(max_tweet_id, tweet_id)
                        max_dt = status['created_at']

                n_tweets = tweetservice.get_number_of_queued()

                tweetservice.commit()

                self.log.debug('Found %d tweets.' % (n_tweets))

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

                self.wait.wait(1)
                    
    
    def cleanup(self):
        self.log.info('Caught interrupt signal. Exiting...')
        self.wait.set()
        scanservice.done(int(time.time()))

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    log = logging.getLogger('smisc.manager')
    fd = open(config['bot']['log'], 'a', 1)
    handler = logging.StreamHandler(fd)
    formatter = logging.Formatter('%(asctime):%(name)s:%(levelname): %(message)s')
    handler.setFormatter(formatter)
    mhandler = logging.handlers.MemoryHandler(0, target=handler)
    log.addHandler(handler)
    log.setLevel(50)

    logging.info('SMISC Manager started')

    api = TwitterAPI(config['twitter-manager']['key'], config['twitter-manager']['secret'], auth_type='oAuth2')

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    manager = ManagerMain(log, api, dbc, rds)
    try:
        manager.main()
    except Exception as err:
        log.exception('Caught error: %s' % (str(err)))
        manager.cleanup()
