import configparser
import datetime
import psycopg2
import redis
import sys

from TwitterAPI import TwitterAPI

from common.filtr import FilterJob
from common.filtr import FilterService

from common.scraper import ScrapeJob
from common.scraper import ScrapeService

import time

def main(api, dbc, rds, logfile):
    while True:
        time.sleep(1)

if __name__ == "__main__":
    print("Pacsocial Twitter Scraper")

    config = configparser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    logfile = open(config['bot']['log'], 'a+')
    sys.stdout = logfile
    sys.stderr = logfile

    print("Pacsocial Twitter Scraper started at %s" % (datetime.datetime.now().strftime("%b %d %H:%M:%S")), file=logfile)

    api = TwitterAPI(config['twitter-manager']['key'], config['twitter-manager']['secret'], auth_type='oAuth2')

    dbc = psycopg2.connect(user=config['postgres']['username'], database=config['postgres']['database'], host=config['postgres']['host'])
    dbc.autocommit = True
    rds = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=int(config['redis']['database']))

    main(api, dbc, rds, logfile)
