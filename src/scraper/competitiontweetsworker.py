from ratelimit import ProtectedException

import time
import threading
import logging
import queue

class CompetitionTweetsScraperWorker(threading.Thread):
    def __init__(self, scrapeservice, rlapi, tweetservice):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.tweetservice = tweetservice
        self.scrapeservice = scrapeservice

    def run(self):
        try:
            job = self.scrapeservice.dequeue()
            if job is None:
                return

            (user_id, since_id) = (job["user_id"], job["since_id"])

            last_tweets = self.tweetservice.tweets_where('user_id = %s', [user_id], 1, 'tweet_id desc')

            last_tweet_id = None

            if len(last_tweets):
                last_tweet_id = last_tweets[0]['tweet_id']

                if since_id is not None:
                    since_id = max(since_id, last_tweet_id)
                else:
                    since_id = last_tweet_id

            if since_id is None:
                logging.info('Getting tweets for %s, starting with whenever', user_id)
            else:
                logging.info('Getting tweets for %s, starting with %d', user_id, since_id)

            params = {'user_id': user_id, 'count': 200}

            if since_id is not None and since_id > 0:
                params['since_id'] = since_id

            try:
                resp = self.rlapi.request('statuses/user_timeline', params)
            except ProtectedException as e:
                logging.info('%s is protected', user_id)
                return

            for tweet in resp:
                self.tweetservice.queue_tweet(tweet, False)

                if since_id is None:
                    since_id = tweet['id']
                else:
                    since_id = max(since_id, tweet['id'])

            tweets = len(resp)
            self.tweetservice.commit()

            logging.info('Wrote %d tweets', tweets)

            if tweets > 0:
                self.scrapeservice.enqueue({
                    "user_id": user_id,
                    "since_id": since_id
                })

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))

