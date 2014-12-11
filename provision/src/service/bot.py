import time

from model import Model

class BotService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "team_bot")

    def get_bots(self):
        self.db.execute('select * from "team_bot" where type=0 and kill_date IS NULL')
        return self._fetch_all()
    
    def kill(self, twitter_id):
        now = int(time.time())
        self.db.execute('UPDATE team_bot SET kill_date = %s WHERE twitter_id = %s', (now, twitter_id))
