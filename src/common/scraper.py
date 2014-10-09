import threading
import time

class ScrapeJob(threading.Thread):
    def __init__(self, rlapi, edgeservice, scrapeservice, scanservice, filterservice):
        threading.Thread.__init__(self)
        self.rlapi = rlapi
        self.scrapeservice = scrapeservice
        self.filterservice = filterservice
        self.scanservice = scanservice
        self.edgeservice = edgeservice
        self.aborted = False
    def abort(self):
        self.aborted = True
    def run(self):
        while not self.aborted:
            job = self.scrapeservice.dequeue()
            if job:
                cursor = -1
                (twitter_id, breadth) = job
                print("Scraping (breadth = %d)..." % (breadth))
                self.filterservice.mark_user_scanned(twitter_id)
                follower_ids = []
                while True:
                    resp = self.rlapi.request('followers/ids', {'user_id': twitter_id, 'count': 5000, 'cursor': cursor})
                    for follower in resp.get_iterator():
                        resp_follower_ids = []

                        if 'ids' in follower:
                            for follower_id in follower['ids']:
                                resp_follower_ids.append(str(follower_id))
                                follower_ids.append(str(follower_id))

                            self.edgeservice.add_follower_edges(twitter_id, resp_follower_ids)
                            cursor = follower['next_cursor']

                    if cursor <= 0:
                        break

                for follower_id in follower_ids:
                    self.filterservice.push(follower_id, breadth+1)

            time.sleep(1)

class ScrapeService:
    def __init__(self, rds):
        self.rds = rds
        self.scan = None
    def set_current_scan(self, scan):
        self.scan = scan
    def enqueue(self, twitter_id, depth):
        self.rds.lpush('scan_%d_scrape_%d' % (self.scan.getId(), depth), twitter_id)
    def dequeue(self):
        if self.scan is not None:
            for breadth in range(self.scan.getMaxBreadth()+1):
                twitter_id = self.rds.lpop('scan_%d_scrape_%d' % (self.scan.getId(), breadth))
                if twitter_id is not None:
                    return (int(twitter_id), breadth)
    def erase(self):
        for breadth in range(self.scan.getMaxBreadth()):
            self.rds.delete('scan_%d_scrape_%d' % (self.scan.getId(), breadth))
    def length(self):
        total = 0
        for breadth in range(0, self.scan.getMaxBreadth()+1):
            total += int(self.rds.llen('scan_%d_scrape_%d' % (self.scan.getId(), breadth)))
        return total
