from util import twittertime as twittertime

class TweetService:
    def __init__(self, db):
        self.db = db
        self.tweets = []
        self.entities = []
    def get_latest_tweet_id(self):
        self.db.execute('select MAX(tweet_id) from "tweet"')
        rslt = self.db.fetchone()
        if rslt is not None and rslt[0] is not None:
            return int(rslt[0])
        return None

    def tweets_where(self, where, args = [], limit = 100, order_by = 'tweet_id asc'):
        args = args + [limit]
        result = self.db.execute('select tweet_id, user_id, text, timestamp from "tweet" where ' + where + ' order by ' + order_by + ' limit %s', tuple(args))
        results = self.db.fetchall()
        tweets = []
        if results is not None:
            for result in results:
                tweets.append({
                    "tweet_id": int(result[0]),
                    "user_id": result[1],
                    "text": result[2],
                    "timestamp": int(result[3])
                })
            return tweets
        return []

    def queue_tweet(self, status, interesting):
        tweet_id = int(status["id"])
        text = status["text"]
        timestamp = twittertime(status['created_at'])
        user = status["user"]
        user_id = user["id_str"]
        self.tweets.append((tweet_id, user_id, text, timestamp, interesting))

        if "urls" in status["entities"] and len(status["entities"]["urls"]) > 0:
            for url in status["entities"]["urls"]:
                self.entities.append( (tweet_id, "url", url["url"]) )

        if "hashtags" in status["entities"] and len(status["entities"]["hashtags"]) > 0:
            for htag in status["entities"]["hashtags"]:
                self.entities.append( (tweet_id, "hashtag", htag["text"]) )

        if "user_mentions" in status["entities"] and len(status["entities"]["user_mentions"]) > 0:
            for mention in status["entities"]["user_mentions"]:
                self.entities.append( (tweet_id, "mention", mention["id_str"]) )

    def get_number_of_queued(self):
        return len(self.tweets)

    def commit(self):
        if len(self.tweets) > 0:
            self.db.executemany('INSERT INTO "tweet" (tweet_id, user_id, text, timestamp, interesting) VALUES(%s, %s, %s, %s, %s)', self.tweets)
        if len(self.entities) > 0:
            self.db.executemany('INSERT INTO "tweet_entity" (tweet_id, "type", text) VALUES(%s, %s, %s)', self.entities)

        self.tweets = []
        self.entities = []
