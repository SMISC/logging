import re
import logging

class Scoring:
    TYPE_REPLY = 'reply'
    TYPE_LINKSHARE = 'link'

    def __init__(self, lockservice, botservice, teamlinkservice, tweetservice, scoreservice, stats):
        self.lockservice = lockservice
        self.botservice = botservice
        self.teamlinkservice = teamlinkservice
        self.tweetservice = tweetservice
        self.scoreservice = scoreservice
        self.stats = stats

    def main(self):
        if not self.lockservice.acquire():
            return
        
        self.bots = self.botservice.get_bots()
        self.links = self.teamlinkservice.get_links()
        self.last_tweet_psqlid = self.scoreservice.get_last_score_ref_id()

        tweets_entities = self.tweetservice.get_scoring_entities(self.bots, self.last_tweet_psqlid)

        max_tweet_id = -1

        for entity in tweets_entities:
            max_tweet_id = max(max_tweet_id, int(entity['tweet_id']))

            if entity['type'] == 'mention':
                for bot in self.bots:
                    if bot['twitter_id'] == entity['text'].strip():
                        logging.info('bot %s scored a reply!', entity['text'])
                        self.stats.log_point('score.mention.' + str(bot['team_id']), entity['timestamp'])
                        self.scoreservice.score(bot['team_id'], bot['twitter_id'], self.TYPE_REPLY, entity['tweet_id'])
                        break
            elif entity['type'] == 'url':
                for link in self.links:
                    if link['link'].strip() == entity['text'].strip():
                        logging.info('team %s scored a retweet of %s on tweet id %s!', link['team_id'], entity['text'], entity['tweet_id'])
                        self.stats.log_point('score.link.' + str(link['team_id']), entity['timestamp'])
                        self.scoreservice.score(link['team_id'], None, self.TYPE_LINKSHARE, entity['tweet_id'])
                        break

        self.scoreservice.mark_last_score_ref_id(max_tweet_id)
