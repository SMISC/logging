import logging
import time
import json

class StatsClient:
    def __init__(self, ifdb, app):
        self.ifdb = ifdb
        self.app = app
        self.points = []

    def flush(self):
        self.ifdb.write_points(self.points)

    def log_loadavg(self, one, five, fifteen):
        self.points.append({
            "points": [
                [one, five, fifteen]
            ],
            "name": "machine.load",
            "columns": ["one", "five", "fifteen"]
        })

    def log_memory(self, free, total):
        self.points.append({
            "points": [
                [free, total]
            ],
            "name": "machine.memory",
            "columns": ["free", "total"]
        })

    def log_app_return(self, code):
        self.points.append({
            "points": [
                [code]
            ],
            "name": "app.return",
            "columns": ["code"]
        })

    def log_twitter_response(self, url, status_code, elapsed):
        self.points.append({
            "points": [
                [url, status_code, elapsed]
            ],
            "name": "twitter.response",
            "columns": ["url", "status", "elapsed"]
        })
    
    def log_throughput(self, sent, recv):
        self.points.append({
            "points": [
                [sent, recv]
            ],
            "name": "machine.net",
            "columns": ["sent", "recv"]
        })

    def log_point(self, what, when, howmany = 1):
        self.points.append({
            "points": [
                [when, howmany]
            ],
            "name": "app." + what,
            "columns": ["time", "count"] 
        })

    def log_diskusage(self, free, total):
        self.points.append({
            "points": [
                [free, total]
            ],
            "name": "machine.disk",
            "columns": ["free", "total"]
        })

    def log_exception(self, context = 'app', subcontext = ''):
        if '' != subcontext:
            subcontext = '.' + subcontext

        self.points.append({
            "points": [
                [1]
            ],
            "name": "app.exception." + context + subcontext,
            "columns": ["count"]
        })

    def log_queue_length(self, which, length):
        self.points.append({
            "points": [
                [length]
            ],
            "name": "app.queuelength." + which,
            "columns": ["length"]
        })
