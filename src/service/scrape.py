import json
import logging
import time

class ScrapeService:
    def __init__(self, rds, key):
        self.rds = rds
        self.key = key
    def enqueue(self, item):
        self.rds.lpush(self.key, json.dumps(item))
    def dequeue(self):
        result = self.rds.lpop(self.key)
        if result:
            return json.loads(result)
    def length(self):
        return int(self.rds.llen(self.key))
