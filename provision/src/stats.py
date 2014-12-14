import logging
import time
import json

class StatsClient:
    def __init__(self, ifdb, app):
        self.ifdb = ifdb
        self.app = app

    def log_app_return(self, code):
        self.ifdb.write_points([{
            "points": [
                [code]
            ],
            "name": "app.return",
            "columns": ["code"]
        }])

    def log_twitter_response(self, url, status_code, elapsed):
        self.ifdb.write_points([{
            "points": [
                [url, status_code, elapsed]
            ],
            "name": "twitter.response",
            "columns": ["url", "status", "elapsed"]
        }])
    
    def log_exception(self, context = 'app', subcontext = ''):
        if '' != subcontext:
            subcontext = '.' + subcontext

        self.ifdb.write_points([{
            "points": [
                [1]
            ],
            "name": "app.exception." + context + subcontext,
            "columns": ["count"]
        }])

    def log_queue_length(self, which, length):
        self.ifdb.write_points([{
            "points": [
                [length]
            ],
            "name": "scan." + which,
            "columns": ["length"]
        }])
