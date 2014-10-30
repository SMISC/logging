import logging
import time

class RecentTweetsScraper:
    def __init__(self, tweetservice, userservice, scrapeservice):
        self.tweetservice = tweetservice
        self.userservice = userservice
        self.scrapeservice = scrapeservice

    def main(self):
        last_tweet_id = 0
        
        while True:
            logging.info('Polling for tweets > %d' % (last_tweet_id))
            recent_tweets = self.tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            
            user_ids = []
            for tweet in recent_tweets:
                user_ids.append(tweet['user_id'])
                last_tweet_id = max(last_tweet_id, tweet['tweet_id'])

            user_ids_set = set(user_ids)

            for user_id in user_ids_set:
                if not self.scrapeservice.is_user_queued(user_id):
                    self.scrapeservice.enqueue('follow', user_id)
                    self.scrapeservice.mark_queued(user_id)

            time.sleep(2)
