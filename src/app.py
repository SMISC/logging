import psycopg2
import redis
import sys
import logging
import logging.handlers
import configparser

from ratelimit import RateLimitedTwitterAPI

from service.scrape import ScrapeService
from service.tweet import TweetService
from service.user import UserService
from service.edge import EdgeService
from service.lock import LockService

from scraper.needsmeta import NeedsMetaScraper
from scraper.channel import ChannelScraper
from scraper.info import InfoScraper
from scraper.followers import FollowersScraper
from scraper.competitiontweets import CompetitionTweetsScraper

class SMISC:
    def __init__(self, app):
        self.config = configparser.ConfigParser()
        self.config.read('/usr/local/share/smisc.ini')
        self.log = logging.getLogger(None)
        self.rds = None
        self.dbc = None
        self.locks = []

    def setupLogging(self, level):
        handler = logging.handlers.RotatingFileHandler(self.config['smisc']['log'], maxBytes=1024*1024*10, backupCount=5)
        formatter = logging.Formatter('{asctime}\t{name}\t{levelname}\t\t{message}', style='{')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        stdout_handler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(stdout_handler)

        self.log.setLevel(level)

        logging.getLogger('requests').setLevel(logging.ERROR)

    def getConfig(self):
        return self.config

    def getRedis(self):
        if self.rds is None:
            self.rds = redis.StrictRedis(host=self.config['redis']['host'], port=self.config['redis']['port'], db=int(self.config['redis']['database']))
        return self.rds
        
    def getDatabase(self):
        if self.dbc is None:
            self.dbc = psycopg2.connect(user=self.config['postgres']['username'], database=self.config['postgres']['database'], host=self.config['postgres']['host'])
            self.dbc.autocommit = True
        return self.dbc
        
    def getDatabaseCursor(self):
        dbc = self.getDatabase()
        return dbc.cursor()
    
    def getTwitterAPI(self):
        keys = self.config['twitter']['keys'].split("\n")
        secrets = self.config['twitter']['secrets'].split("\n")
        return RateLimitedTwitterAPI(list(zip(keys, secrets)))

    def getService(self, which, *args):
        if 'tweet' == which:
            return TweetService(self.getDatabaseCursor())
        elif 'user' == which:
            return UserService(self.getDatabaseCursor())
        elif 'scrape' == which:
            return ScrapeService(self.getRedis(), args[0])
        elif 'edge' == which:
            return EdgeService(self.getDatabaseCursor())
        elif 'lock' == which:
            service = LockService(self.getRedis(), args[0])
            self.locks.append(service)
            return service

    def getProgram(self, which):
        if 'channel' == which:
            rlapi = self.getTwitterAPI()
            tweetservice = self.getService('tweet')
            lockservice = self.getService('lock')
            return ChannelScraper(rlapi, tweetservice, lockservice)

        elif 'followers' == which:
            clients = []
            edgeservices = []
            scrapeservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(15):
                clients.append(self.getTwitterAPI())
                edgeservices.append(self.getService('edge'))
                scrapeservices.append(self.getService('scrape', 'followers'))

            scrapeservices.append(self.getService('scrape', 'followers')) # append an extra for main thread 
            return FollowersScraper(clients, edgeservices, userservice, lockservice, scrapeservices)

        elif 'competition-tweets' == which:
            clients = []
            tweetservices = []
            scrapeservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(15):
                clients.append(self.getTwitterAPI())
                tweetservices.append(self.getService('tweet'))
                scrapeservices.append(self.getService('scrape', 'tweets'))

            scrapeservices.append(self.getService('scrape', 'followers')) # append an extra for main thread 

            return CompetitionTweetsScraper(clients, tweetservices, userservice, lockservice, scrapeservices)

        elif 'clean' == which:
            pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 -m app [channel | followers | competition-tweets]')
        sys.exit(1)

    app_name = sys.argv[1]

    smisc = SMISC(app_name)
    smisc.setupLogging(logging.INFO)

    app = smisc.getProgram(app_name)
    if app is None:
        logging.error('Invalid application "%s"' % (app_name))
    else:
        try:
            app.main()
        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))
        finally:
            for lock in self.locks:
                if lock.get_did_acquire():
                    lock.release()
            

