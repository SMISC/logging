import logging
import psycopg2

from model import Model

logger = logging.getLogger(__name__)

class UserService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "tuser")

    def get_competition_users(self, where = 'interesting=TRUE'):
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

    def get_users_between_count(self, id_start, id_end):
        self.db.execute("SELECT count(id) from tuser WHERE id >= %s and id < %s", (id_start, id_end))
        result = self.db.fetchone()
        return int(result[0])

    def get_users_between(self, id_start, id_end, page_num):
        PS = 1E4 # 10,000

        offset = (PS * page_num)
        limit = PS
        self.db.execute("SELECT * from tuser WHERE id >= %s and id < %s order by id asc limit %s offset %s", (id_start, id_end, limit, offset))
        return self._fetch_all()

    def users_where(self, where, args = []):
        result = self.db.execute('select * from tuser where ' + where, tuple(args))
        return self._fetch_all()

    def create_user(self, user):
        uval = (user["user_id"], user["screen_name"], user["full_name"], user["followers"], user["bio"], user["total_tweets"], user["timestamp"], user["following"], user["interesting"], user["location"], user["website"], user["profile_image_url"], user["profile_banner_url"], user["protected"])
        try:
            result = self.db.execute('insert into tuser (user_id, screen_name, full_name, followers, bio, total_tweets, timestamp, following, interesting, location, website, profile_image_url, profile_banner_url, protected) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', uval)
            return True
        except Exception as e:
            logger.exception('Error inserting user: %s', str(e))
            return False
