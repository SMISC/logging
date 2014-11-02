import logging
import time

class NeedsMetaScraper:
    def __init__(self, tweetservice, userservice, scrapeservice, edgeservice):
        self.tweetservice = tweetservice
        self.userservice = userservice
        self.scrapeservice = scrapeservice
        self.edgeservice = edgeservice

    def main(self):
        last_tweet_id = 0
        edge_offset = 0
        
        while True:
            logging.debug('Polling for tweets > %d' % (last_tweet_id))
            recent_tweets = self.tweetservice.tweets_where('tweet_id > %s', [last_tweet_id])
            
            user_ids = []
            for tweet in recent_tweets:
                user_ids.append(tweet['user_id'])
                last_tweet_id = max(last_tweet_id, tweet['tweet_id'])

            user_ids_set = set(user_ids)

            for user_id in user_ids_set:
                self.scrapeservice.enqueue('follow', user_id)
                self.scrapeservice.enqueue('info', user_id)

            logging.debug('Polling for edges (set %d)' % (edge_offset))
            edges = self.edgeservice.get_edges(edge_offset)
            for edge in edges:
                self.scrapeservice.enqueue('info', edge['to_user'])
                self.scrapeservice.enqueue('info', edge['from_user'])
            edge_offset += len(edges)

            time.sleep(2)
