from model import Model

class ScoreService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "point")

    def get_last_score_ref_id(self):
        self.db.execute('select MAX(entity_ref) from "point"')
        result = self.db.fetchone()
        return result[0]

    def score(self, bot_id, typ, ref_id):
        self.db.execute('INSERT INTO point (bot_id, type, entity_ref) VALUES (%s, %s, %s)', (bot_id, typ, ref_id))
