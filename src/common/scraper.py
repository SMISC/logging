import threading
import time

class ScrapeJob(threading.Thread):
    def __init__(self, rlapi, edgeservice, scrapeservice, logfile):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.edgeservice = edgeservice
        self.logfile = logfile
        self.aborted = False
    def abort(self):
        self.aborted = True
    def run(self):
        while not self.aborted:
            print("[scraper-followers] Scraping", file=self.logfile)
            user_id = self.scrapeservice.dequeue()
            if user_id:
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

            time.sleep(1)

class ScrapeService:
    def __init__(self, rds):
        self.rds = rds
        self.scan_id = None
        self.max_depth = None
    def set_current_scan_id(self, scan_id):
        self.scan_id = scan_id
    def is_user_queued(self, user_id):
        return self.rds.sismember('scrape_%d_progress' % (self.scan_id), user_id)
    def enqueue(self, user_id):
        self.rds.sadd('scrape_%d_progress' % (self.scan_id), user_id)
        self.rds.lpush('scrape_%d_queue' % (self.scan_id), user_id)
    def dequeue(self):
        result = self.rds.lpop('scrape_%d_queue' % (self.scan_id))
        if result:
            return int(result)
    def finished(self, user_id):
        self.rds.srem('scrape_%d_progress' % (self.scan_id), user_id)
    def length(self):
        return int(self.rds.llen('scrape_%d_queue' % (self.scan_id)))
    def total_processed(self):
        return int(self.rds.scard('scrape_%d_progress' % (self.scan_id)))
    def erase(self):
        self.rds.delete('scrape_%d_progress' % (self.scan_id), 'scrape_%d_queue' % (self.scan_id))
