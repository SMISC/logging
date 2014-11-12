import logging
import psycopg2

class UserService:
    def __init__(self, db):
        self.db = db

    def users_where(self, where, args = [], order_by = None, lim = None, offset = None):
        query = 'select user_id, screen_name, full_name, followers, following, bio, timestamp, total_tweets from tuser where ' + where
        if order_by is not None:
            query += ' order by ' + order_by
        if lim is not None:
            query += ' limit %s' % (lim,)

            if offset is not None:
                query += ' offset %d' % (offset,)

        result = self.db.execute(query, tuple(args))
        try:
            results = self.db.fetchall()
        except psycopg2.ProgrammingError:
            return []

        users = []
        if results is not None:
            for result in results:
                users.append({
                    "user_id": int(result[0]),
                    "screen_name": result[1],
                    "full_name": result[2],
                    "followers": int(result[3]),
                    "following": int(result[4]),
                    "bio": result[5],
                    "timestamp": int(result[6]),
                    "total_tweets": int(result[7])
                })
            return users

        return []

    def create_user(self, user):
        uval = (user["user_id"], user["screen_name"], user["full_name"], user["followers"], user["bio"], user["total_tweets"], user["timestamp"], user["following"])
        try:
            result = self.db.execute('insert into tuser (user_id, screen_name, full_name, followers, bio, total_tweets, timestamp, following) values (%s, %s, %s, %s, %s, %s, %s, %s)', uval)
            return True
        except Exception as e:
            logging.exception('Error inserting user: %s', str(e))
            return False
