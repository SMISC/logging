import json
import time
import threading

class FilterService:
    def __init__(self, rds, db):
        self.rds = rds
        self.db = db
        self.scan = None
    def set_current_scan(self, scan):
        self.scan = scan
        self.rds.set('current_scan', scan.getId())
    def push(self, twitter_id, depth):
        if depth <= self.scan.getMaxBreadth():
            self.rds.lpush('scan_%d_filter' % (self.scan.getId()), json.dumps([twitter_id, depth]))
    def pop(self, n):
        rslts = []
        for i in range(n):
            top = self.rds.lpop('scan_%d_filter' % (self.scan.getId()))
            if top:
                rslts.append(json.loads(top.decode('utf8')))
        return rslts
    def length(self):
        return int(self.rds.llen('scan_%d_filter' % (self.scan.getId())))
    def is_user_scanned(self, twitter_id):
        return self.rds.sismember('scan_%d_users' % (self.scan.getId()), twitter_id)
    def mark_user_scanned(self, twitter_id):
        self.rds.sadd('scan_%d_users' % (self.scan.getId()), twitter_id)
    def erase(self):
        self.rds.delete('scan_%d_filter' % (self.scan.getId()))
        self.rds.delete('scan_%d_users' % (self.scan.getId()))

class FilterJob(threading.Thread):
    def __init__(self, filterservice, scanservice, scrapeservice):
        threading.Thread.__init__(self)
        self.filterservice = filterservice
        self.scanservice = scanservice
        self.scrapeservice = scrapeservice
        self.aborted = False
    def abort(self):
        self.aborted = True
    def run(self):
        while not self.aborted:
            top = self.filterservice.pop(100)
            twitter_ids = []
            depths = {}
            avg_depth = 0
            for item in top:
                (twitter_id, depth) = item
                twitter_id = str(twitter_id)
                twitter_ids.append(twitter_id)
                depths[twitter_id] = depth
                avg_depth += depth

            if len(twitter_ids):
                avg_depth /= len(twitter_ids)
                print("Filtering %d users with average depth %0.2f" % (len(twitter_ids), avg_depth))
                for twitter_id in twitter_ids:
                    if not self.filterservice.is_user_scanned(twitter_id):
                        self.scrapeservice.enqueue(twitter_id, depths[twitter_id])
            time.sleep(1)
