from model import Model

class BotService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "team_bot")

    def get_bots(self):
        self.db.execute('select * from "team_bot" where type=0')
        results = self.db.fetchall()
        return results
