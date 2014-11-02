import logging
import time

class EdgeService:
    def __init__(self, db):
        self.db = db
    def add_follower_edges(self, followed_id, follower_ids):
        edges = []
        for follower_id in follower_ids:
            edges.append((time.time(), follower_id, followed_id))

        try:
            self.db.executemany('INSERT INTO tuser_tuser (timestamp, from_user, to_user, weight) VALUES (%s, %s, %s, 1)', edges)
        except Exception as e:
            logging.exception('Error inserting user-user edges: %s', str(e))
    def get_edges(self, offset = 0, limit = 100):
        self.db.execute("SELECT to_user, from_user FROM tuser_tuser order by timestamp asc limit %s offset %s", (limit, offset))
        try:
            results = self.db.fetchall()
        except psycopg2.ProgrammingError:
            return []

        edges = []
        for result in results:
            edges.append({
                'to_user': result[0],
                'from_user': result[1]
            })
        return edges
