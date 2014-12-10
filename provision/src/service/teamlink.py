from model import Model

class TeamLinkService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "team_link")

    def get_links(self):
        self.db.execute('select * from "team_link"')
        results = self.db.fetchall()
        return results
