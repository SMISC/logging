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
