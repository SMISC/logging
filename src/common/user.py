import logging

class UserService:
    def __init__(self, db):
        self.db = db

    def users_where(self, where, args = []):
        result = self.db.execute('select user_id, screen_name, full_name, followers, following, bio, timestamp, total_tweets from tuser where ' + where, tuple(args))
        results = self.db.fetchall()
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
            logging.exception('Error inserting user: %s\nData: %s\n\n', str(e), str(uval))
            return False
