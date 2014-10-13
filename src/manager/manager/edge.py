class EdgeService:
    def __init__(self, rds, db):
        self.rds = rds
        self.db = db
        self.cur_scan_id = None
    def set_current_scan_id(self, scan_id):
        self.cur_scan_id = scan_id
    def add_follower_edges(self, followed_id, follower_ids):
        edges = []
        for follower_id in follower_ids:
            edges.append((self.cur_scan_id, follower_id, followed_id))
        self.db.executemany('INSERT INTO "user_user" (scan_id, from_user, to_user, weight) VALUES (%s, %s, %s, 1)', edges)
