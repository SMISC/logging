import threading
import time
import sys

from common.time import twittertime as twittertime

class ScrapeFollowersJob(threading.Thread):
    def __init__(self, rlapi, edgeservice, scrapeservice, evt, logfile):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.edgeservice = edgeservice
        self.evt = evt
        self.logfile = logfile
    def run(self):
        sys.stdout = self.logfile
        sys.stderr = self.logfile
        while not self.evt.is_set():
            user_id = self.scrapeservice.dequeue('follow')
            if user_id:
                print("[scraper-followers] Scraping %d" % (user_id))
                sys.stdout.flush()
                cursor = -1
                follower_ids = []
                while True:
                    resp = self.rlapi.request('followers/ids', {'user_id': user_id, 'count': 5000, 'cursor': cursor})
                    for follower in resp.get_iterator():
                        resp_follower_ids = []

                        if 'ids' in follower:
                            for follower_id in follower['ids']:
                                resp_follower_ids.append(str(follower_id))
                                follower_ids.append(str(follower_id))

                            self.edgeservice.add_follower_edges(user_id, resp_follower_ids)
                            cursor = follower['next_cursor']

                    if cursor <= 0:
                        break

class ScrapeInfoJob(threading.Thread):
    def __init__(self, rlapi, userservice, scrapeservice, evt, logfile):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.userservice = userservice
        self.evt = evt
        self.logfile = logfile
    def run(self):
        sys.stdout = self.logfile
        sys.stderr = self.logfile
        while not self.evt.is_set():
            ids = []
            t = 15 # wait up to 15 seconds, otherwise we're behind on average
            while not self.evt.is_set() and len(ids) < 100 and t > 0:
                user_id = self.scrapeservice.dequeue('info')
                if user_id:
                    ids.append(int(user_id))
                t = t - 1
                self.evt.wait(1)
            if len(ids) > 0:
                print('[scraper-info] Scraping %d' % (len(ids)))
                sys.stdout.flush()
                resp = self.rlapi.request('users/lookup', {'user_id': ','.join(ids)})
                for user in resp.get_iterator():
                    self.userservice.create_user({
                        'user_id': user['id'],
                        'screen_name': user['screen_name'],
                        'total_tweets': user['statuses_count'],
                        'followers': user['followers_count'],
                        'following': user['friends_count'],
                        'full_name': user['name'],
                        'bio': user['description'],
                        'timestamp': twittertime(user['created_at'])
                    })

class ScrapeService:
    def __init__(self, rds, scan_id):
        self.rds = rds
        self.scan_id = scan_id
    def set_current_scan_id(self, scan_id):
        self.scan_id = scan_id
    def is_user_queued(self, user_id):
        return self.rds.sismember('scrape_%d_progress' % (self.scan_id), user_id)
    def enqueue(self, user_id):
        self.rds.sadd('scrape_%d_progress' % (self.scan_id), user_id)
        self.rds.lpush('scrape_%d_queue_follow' % (self.scan_id), user_id)
        self.rds.lpush('scrape_%d_queue_info' % (self.scan_id), user_id)
    def dequeue(self, which):
        result = self.rds.lpop('scrape_%d_queue_%s' % (self.scan_id, which))
        if result:
            return int(result)
    def finished(self, user_id):
        self.rds.srem('scrape_%d_progress' % (self.scan_id), user_id)
    def length(self, which):
        return int(self.rds.llen('scrape_%d_queue_%s' % (self.scan_id, which)))
    def total_processed(self):
        return int(self.rds.scard('scrape_%d_progress' % (self.scan_id)))
    def erase(self, whiches):
        for which in whiches:
            self.rds.delete('scrape_%d_queue_%s' % (self.scan_id, which))
        self.rds.delete('scrape_%d_progress' % (self.scan_id))
