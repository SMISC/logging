from ratelimit import ProtectedException
from ratelimit import OverLimits

import time
import threading
import logging
import queue

from util import twittertime as twittertime

logger = logging.getLogger(__name__)

class CompetitionTweetsScraperWorker(threading.Thread):
    def __init__(self, scrapeservice, rlapi, tweetservice, stats):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.tweetservice = tweetservice
        self.scrapeservice = scrapeservice
        self.stats = stats

    def run(self):
        try:
            job = self.scrapeservice.dequeue()
            if job is None:
                return

            (user_id, job_since_id) = (job["user_id"], job["since_id"])

            since_id = job_since_id

            last_tweets = self.tweetservice.tweets_where('user_id = %s', [user_id], 1, 'tweet_id desc')

            last_tweet_id = None

            if len(last_tweets):
                last_tweet_id = last_tweets[0]['tweet_id']

                if since_id is not None:
                    since_id = max(since_id, last_tweet_id)
                else:
                    since_id = last_tweet_id

            if since_id is None:
                logger.debug('Getting tweets for %s, starting with whenever', user_id)
            else:
                logger.debug('Getting tweets for %s, starting with %d', user_id, since_id)

            params = {'user_id': user_id, 'count': 200}

            if since_id is not None and since_id > 0:
                params['since_id'] = since_id

            try:
                resp = self.rlapi.request('statuses/user_timeline', params)
            except ProtectedException as e:
                logger.info('%s is protected', user_id)
                return
            except OverLimits:
                self.scrapeservice.enqueue({
                    "user_id": user_id,
                    "since_id": job_since_id
                })
                return

            for tweet in resp:
                self.tweetservice.queue_tweet(tweet, False)

                try:
                    self.stats.log_point('tweet', twittertime(tweet['created_at']))
                except:
                    pass

                if since_id is None:
                    since_id = tweet['id']
                else:
                    since_id = max(since_id, tweet['id'])

            tweets = len(resp)
            self.tweetservice.commit()

            if tweets > 0:
                self.scrapeservice.enqueue({
                    "user_id": user_id,
                    "since_id": since_id
                })

        except Exception as err:
            logger.exception('Caught error: %s' % (str(err)))

