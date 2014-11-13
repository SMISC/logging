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
            user_id = self.scrapeservice.dequeue()
            if user_id is None:
                return

            last_tweets = self.tweetservice.tweets_where('user_id = %s', [user_id], 1, 'tweet_id desc')

            last_tweet_id = 0

            if len(last_tweets):
                last_tweet_id = last_tweets[0]['tweet_id']

            pagen = 0
            tweets = 0
            since_id = last_tweet_id

            while tweets > 0 or pagen is 0:
                logging.info('Getting %dth page of tweets for %s, starting with %d', pagen, user_id, since_id)
                pagen += 1

                resp = self.rlapi.request('statuses/user_timeline', {'since_id': since_id, 'user_id': user_id, 'count': 200})
                for tweet in resp:
                    self.tweetservice.queue_tweet(tweet, False)
                    since_id = max(since_id, tweet['id'])

                tweets = len(resp)
                logging.info('Got %d tweets' % (tweets))
                self.tweetservice.commit()
                time.sleep(5)

        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))

