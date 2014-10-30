import logging

class ChannelScraper:
    def __init__(self, rlapi, tweetservice):
        self.rlapi = rlapi
        self.tweetservice = tweetservice

    def main(self):
        while True:
            query = '#vaxtruth OR #vaccinedebate OR #hearthiswell OR #cdcfraud OR #vaccinescauseautism OR #cdcfraudexposed OR #cdccoverup OR #cdcwhistleblower OR #parentsdothework OR #saynotovaccines OR #vaccineeducated'
            max_id = None
            since_id = self.tweetservice.get_latest_tweet_id()

            since_dt = 'the beginning of time'
            max_dt = ''

            while True:
                if max_id is None and since_id is None:
                    # first query ever
                    logging.info('Seeking any tweets we can get.')
                    results = self.rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100})
                elif max_id is not None: # seeking old
                    logging.info('Seeking old tweets before %s (%d)', max_dt, max_id)
                    results = self.rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100, 'max_id': max_id})
                else: # seeking new
                    logging.info('Seeking new tweets since %s (%d)', since_dt, since_id)
                    results = self.rlapi.request('search/tweets', {'include_entities': True, 'result_type': 'recent', 'q': query, 'count': 100, 'since_id': since_id})

                entities = []
                max_tweet_id = None
                min_tweet_id = None
                min_dt = ''
                max_dt = ''

                for status in results.get_iterator():
                    tweet_id = int(status['id'])

                    self.tweetservice.queue_tweet(status)

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

                n_tweets = self.tweetservice.get_number_of_queued()

                self.tweetservice.commit()

                logging.debug('Found %d tweets', n_tweets)

                if n_tweets < 100:
                    # we got less than expected. switch to polling for new tweets.
                    since_id = self.tweetservice.get_latest_tweet_id()
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

                time.sleep(1)
