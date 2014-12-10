import re
import logging

class Scoring:
    TYPE_REPLY = 'reply'
    TYPE_LINKSHARE = 'link'

    def __init__(self, lockservice, botservice, teamlinkservice, tweetservice, scoreservice):
        self.lockservice = lockservice
        self.botservice = botservice
        self.teamlinkservice = teamlinkservice
        self.tweetservice = tweetservice
        self.scoreservice = scoreservice

    def main(self):
        if not self.lockservice.acquire():
            return
        
        self.bots = self.botservice.get_bots()
        self.links = self.teamlinkservice.get_links()
        self.last_tweet_psqlid = self.scoreservice.get_last_score_ref_id()

        logging.info('last scored tweet: %d', self.last_tweet_psqlid)

        self.tweets_entities = self.tweetservice.get_scoring_entities(self.last_tweet_psqlid, self.bots)

        logging.info('there are %d new unscored tweets', len(self.tweets_entities))

        self._do_reply()
        self._do_link_share()

    def _do_reply(self):
        for entity in self.tweets_entities:
            if entity['type'] == 'mention':
                for bot in self.bots:
                    if bot['bot_id'] == entity['text'].strip():
                        logging.info('bot %s scored a reply!', entity['text'])
                        self.scoreservice.score(bot['bot_id'], self.TYPE_REPLY, entity['tweet_id'])
                        break
                

    def _do_link_share(self):
        for entity in self.tweets_entities:
            if entity['type'] == 'url':
                for link in self.links:
                    if link['link'].strip() == entity['text'].strip():
                        logging.info('team %s scored a retweet of %s on tweet id %s!', link['team_id'], entity['text'], entity['tweet_id'])
                        self.scoreservice.score(bot['bot_id'], self.TYPE_REPLY, entity['tweet_id'])
                        break
