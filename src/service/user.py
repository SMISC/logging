import logging
import psycopg2

class UserService:
    def __init__(self, db):
        self.db = db

    def get_competition_users(self, where = 'interesting=True'):
        page = 0
        pagesize = 1000
        users = []
        users_this_page = 0

        while page is 0 or users_this_page is not 0:
            self.db.execute('select distinct on (user_id) id, user_id from tuser where ' + where + ' order by user_id, id desc limit %d offset %d' % (pagesize, pagesize*page))

            users_this_page = 0

            try:
                users_results = self.db.fetchall()
            except psycopg2.ProgrammingError:
                users_results = []

            if users_results is None:
                users_results = []

            for user_result in users_results:
                user_id = user_result[1]
                users.append(str(user_id))
                users_this_page += 1

            page = page + 1

        return users

    def users_where(self, where, args = []):
        result = self.db.execute('select user_id, screen_name, full_name, followers, following, bio, timestamp, total_tweets, interesting, location, website, profile_image_url, profile_banner_url, protected from tuser where ' + where, tuple(args))
        try:
            results = self.db.fetchall()
        except psycopg2.ProgrammingError:
            return []

        users = []
        if results is not None:
            for result in results:
                if results[13] is None: # protected
                    results[13] = False
                if results[8] is None: # interesting
                    results[8] = False

                users.append({
                    "user_id": int(result[0]),
                    "screen_name": result[1],
                    "full_name": result[2],
                    "followers": int(result[3]),
                    "following": int(result[4]),
                    "bio": result[5],
                    "timestamp": int(result[6]),
                    "total_tweets": int(result[7]),
                    "interesting": bool(result[8]),
                    "location": result[9],
                    "website": result[10],
                    "profile_image_url": result[11],
                    "profile_banner_url": result[12],
                    "protected": bool(result[13])
                })
            return users

        return []

    def create_user(self, user):
        uval = (user["user_id"], user["screen_name"], user["full_name"], user["followers"], user["bio"], user["total_tweets"], user["timestamp"], user["following"], user["interesting"], user["location"], user["website"], user["profile_image_url"], user["profile_banner_url"], user["protected"])
        try:
            result = self.db.execute('insert into tuser (user_id, screen_name, full_name, followers, bio, total_tweets, timestamp, following, interesting, location, website, profile_image_url, profile_banner_url, protected) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', uval)
            return True
        except Exception as e:
            logging.exception('Error inserting user: %s', str(e))
            return False
