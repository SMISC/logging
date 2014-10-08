import sys
import os
import queue
import threading
import redis
import psycopg2
import time
import configparser

from TwitterAPI import TwitterAPI

from scraper.scan import Scan
from scraper.scan import ScanService

from scraper.filtr import FilterJob
from scraper.filtr import FilterService

from scraper.scraper import ScrapeJob
from scraper.scraper import ScrapeService

from scraper.edge import EdgeService

from scraper.ratelimit import RateLimitedTwitterAPI

def main(api, dbc, rds):
    print("Inspecting rate limit status...")

    rlapi = RateLimitedTwitterAPI(api)
    rlapi.update()

    print("Starting threads...")

    scanservice = ScanService(dbc.cursor())
    start_time = int(time.time())
    max_breadth = 2
    scan = scanservice.new_scan(start_time, max_breadth)
    print("Starting scan %d" % (scan.getId()))

    filterservice = FilterService(rds, dbc.cursor())
    filterservice.set_current_scan(scan)

    scrapeservice = ScrapeService(rds)
    scrapeservice.set_current_scan(scan)

    edgeservice = EdgeService(rds, dbc.cursor())
    edgeservice.set_current_scan(scan)

    threads = []
    threads.append(FilterJob(filterservice, scanservice, scrapeservice))
    threads.append(ScrapeJob(rlapi, edgeservice, scrapeservice, scanservice, filterservice))

    results = rlapi.request('search/tweets', {'q': '#vaxtruth OR #vaccinedebate OR #hearthiswell OR #cdcfraud OR #vaccinescauseautism OR #cdcfraudexposed OR #cdccoverup OR #cdcwhistleblower', 'count': 100})

    queued = 0

    for status in results.get_iterator():
        text = status["text"]
        user = status["user"]
        twitter_id = int(user["id"])
        filterservice.push(twitter_id, 0)

    for thread in threads:
        thread.start()

    try:
        while True:
            time.sleep(10)
            length = scrapeservice.length() + filterservice.length()
            if 0 is length:
                print("Done.")
                for thread in threads:
                    thread.abort()
                break
    except KeyboardInterrupt:
        print("Caught interrupt signal. Exiting...")
        for thread in threads:
            thread.abort()
    
    filterservice.erase()
    scrapeservice.erase()

    scanservice.done(int(time.time()))

    dbc.close()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('/usr/local/share/pacsocial.ini')

    api = TwitterAPI(config['twitter']['key'], config['twitter']['secret'], auth_type='oAuth2')

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    main(api, dbc, rds)
