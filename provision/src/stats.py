import logging
import time
import json

class StatsClient:
    def __init__(self, ifdb):
        self.ifdb = ifdb

    def log_twitter_response(self, url, status_code, elapsed):
        self.ifdb.write_points([{
            "points": [
                [url, status_code, elapsed]
            ],
            "name": "twitter",
            "columns": ["url", "status", "elapsed"]
        }])
    
    def log_queue_length(self, which, length):
        self.ifdb.write_points([{
            "points": [
                [length]
            ],
            "name": "scan." + which,
            "columns": ["length"]
        }])
