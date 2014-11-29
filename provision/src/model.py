class Model:
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def _fetch_all(self):
        results = []

        try:
            results = self.db.fetchall()
        except psycopg2.ProgrammingError:
            return []
        
        dicts = []
        for result in results:
            dicts.append(dict(result))

        return dicts
