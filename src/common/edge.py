import logging

class EdgeService:
    def __init__(self, db):
        self.db = db
        self.cur_scan_id = None
    def set_current_scan_id(self, scan_id):
        self.cur_scan_id = scan_id
    def add_follower_edges(self, followed_id, follower_ids):
        edges = []
        for follower_id in follower_ids:
            edges.append((self.cur_scan_id, follower_id, followed_id))
        try:
            self.db.executemany('INSERT INTO tuser_tuser (scan_id, from_user, to_user, weight) VALUES (%s, %s, %s, 1)', edges)
        except Exception as e:
            logging.exception('Error inserting user-user edges: %s\nData: %s\n\n', str(e), str(edges))
            return False
