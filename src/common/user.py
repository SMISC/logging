class UserService:
    def __init__(self, db):
        self.db = db

    def users_where(self, where, args = []):
        result = self.db.execute('select user_id, screen_name, full_name, followers, bio from "user" where ' + where, tuple(args))
        results = self.db.fetchall()
        users = []
        if results is not None:
            for result in results:
                users.append({
                    "user_id": int(result[0]),
                    "screen_name": result[1],
                    "full_name": result[2],
                    "followers": int(result[3]),
                    "bio": result[4]
                })
            return users
        return []

    def create_user(self, user):
        uval = (user["user_id"], user["screen_name"], user["full_name"], user["followers"], user["bio"])
        result = self.db.execute('insert into "user" (user_id, screen_name, full_name, followers, bio) values (%s, %s, %s, %s, %s)', uval)
