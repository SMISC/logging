import logging
import time

class ScrapeService:
    def __init__(self, rds):
        self.rds = rds
    def is_user_queued(self, user_id, which):
        return self.rds.sismember('scrape_progress_%s' % (which), user_id)
    def enqueue(self, which, user_id):
        if not self.is_user_queued(user_id, which):
            self.rds.lpush('scrape_queue_%s' % (which), user_id)
            self.rds.sadd('scrape_progress_%s' % (which), user_id)
    def dequeue(self, which):
        result = self.rds.lpop('scrape_queue_%s' % (which))
        if result:
            if isinstance(result, bytes):
                result = result.decode('utf-8')
            return result
    def finished(self, user_id, which):
        self.rds.srem('scrape_progress_%s' % (which), user_id)
    def length(self, which):
        return int(self.rds.llen('scrape_queue_%s' % (which)))
    def total_processed(self):
        return int(self.rds.scard('scrape_progress'))
