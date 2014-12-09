import logging
import time
from model import Model

logger = logging.getLogger(__name__)

class EdgeService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "tuser_tuser")

    def add_follower_edges(self, followed_id, follower_ids, bot):
        edges = []
        for follower_id in follower_ids:
            edges.append((time.time(), follower_id, followed_id, bot))

        try:
            parts = []
            params = []

            for edge in edges:
                parts.append('(%s, %s, %s, 1, %s)')
                params.extend(list(edge))

            if len(edges):
                query = 'INSERT INTO ' + self.table + ' (timestamp, from_user, to_user, weight, bot) VALUES ' + (','.join(parts))
                self.db.execute(query, tuple(params))
        except Exception as e:
            logger.exception('Error inserting user-user edges: %s', str(e))

    def get_edges_between_count(self, id_start, id_end):
        self.db.execute("SELECT count(id) from " + self.table + " WHERE id >= %s and id < %s", (id_start, id_end))
        result = self.db.fetchone()
        return int(result[0])

    def get_edges_between(self, id_start, id_end, page_num, PS=1E4):
        offset = (PS * page_num)
        limit = PS

        self.db.execute("SELECT * from " + self.table + " WHERE id >= %s and id < %s order by id asc limit %s offset %s", (id_start, id_end, limit, offset))
        return self._fetch_all()
        
    def get_edges(self, offset = 0, limit = 100):
        self.db.execute("SELECT id, to_user, from_user FROM " + self.table + " order by timestamp asc limit %s offset %s", (limit, offset))
        return self._fetch_all()

class BotEdgeService(EdgeService):
    def __init__(self, db):
        Model.__init__(self, db, "tuser_tuser_bot")

    def add_follower_edges(self, followed_id, follower_ids, bot):
        edges = []
        for follower_id in follower_ids:
            edges.append((time.time(), follower_id, followed_id))

        try:
            parts = []
            params = []

            for edge in edges:
                parts.append('(%s, %s, %s)')
                params.extend(list(edge))

            if len(edges):
                query = 'INSERT INTO ' + self.table + ' (timestamp, from_user, to_user) VALUES ' + (','.join(parts))
                self.db.execute(query, tuple(params))
        except Exception as e:
            logger.exception('Error inserting user-user edges: %s', str(e))
