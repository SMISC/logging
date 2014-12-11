from model import Model

class ScoreService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "point")

    def get_last_score_ref_id(self):
        self.db.execute('select MAX(tweet_id) from "cron_score"')
        result = self.db.fetchone()
        return result[0]

    def score(self, team_id, bot_id, typ, ref_id):
        self.db.execute('INSERT INTO point (team_id, bot_id, type, entity_ref) VALUES (%s, %s, %s, %s)', (team_id, bot_id, typ, ref_id))

    def mark_last_score_ref_id(self, max_tweet_id):
        self.db.execute('INSERT INTO cron_score (tweet_id) VALUES (%s)', (str(max_tweet_id),))
