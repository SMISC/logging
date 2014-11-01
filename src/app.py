import psycopg2
import redis
import sys
import logging
import logging.handlers
import configparser

from TwitterAPI import TwitterAPI

from ratelimit import RateLimitedTwitterAPI

from service.scrape import ScrapeService
from service.tweet import TweetService
from service.user import UserService
from service.edge import EdgeService

from scraper.recenttweets import RecentTweetsScraper
from scraper.channel import ChannelScraper
from scraper.info import InfoScraper
from scraper.followers import FollowersScraper

class SMISC:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('/usr/local/share/smisc.ini')
        self.log = logging.getLogger(None)
        self.rds = None
        self.dbc = None

    def setupLogging(self):
        handler = logging.handlers.RotatingFileHandler(self.config['smisc']['log'], maxBytes=1024*1024*10, backupCount=5)
        formatter = logging.Formatter('{asctime}\t{name}\t{levelname}\t\t{message}', style='{')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        stdout_handler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(stdout_handler)

        self.log.setLevel(logging.DEBUG)

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
        rds = self.getRedis()
        keys = self.config['twitter']['keys'].split("\n")
        secrets = self.config['twitter']['secrets'].split("\n")
        for (key, secret) in zip(keys, secrets):
            inuse_key = 'client_id_%s' % (key)
            try:
                with self.rds.pipeline() as pipe:
                    pipe.watch(inuse_key)
                    ttl = int(pipe.ttl(inuse_key))
                    if ttl <= 0:
                        pipe.multi()
                        pipe.setex(inuse_key, 30, '1')
                        pipe.execute()
                        api = TwitterAPI(key, secret, auth_type='oAuth2')
                        return RateLimitedTwitterAPI.fromUnlimited(api)
            except redis.WatchError:
                continue

        raise Exception('No keys left!')

    def getService(self, which):
        if 'tweet' == which:
            return TweetService(self.getDatabaseCursor())
        elif 'user' == which:
            return UserService(self.getDatabaseCursor())
        elif 'scrape' == which:
            return ScrapeService(self.getRedis())
        elif 'edge' == which:
            return EdgeService(self.getDatabaseCursor())

    def getProgram(self, which):
        if 'recenttweets' == which:
            tweetservice = self.getService('tweet')
            userservice = self.getService('user')
            scrapeservice = self.getService('scrape')
            return RecentTweetsScraper(tweetservice, userservice, scrapeservice)
        elif 'info' == which:
            clients = []
            for i in range(3):
                clients.append(self.getTwitterAPI())
            userservice = self.getService('user')
            scrapeservice = self.getService('scrape')
            return InfoScraper(clients, userservice, scrapeservice)
        elif 'channel' == which:
            rlapi = self.getTwitterAPI()
            tweetservice = self.getService('tweet')
            return ChannelScraper(rlapi, tweetservice)
        elif 'followers' == which:
            clients = []
            for i in range(3):
                clients.append(self.getTwitterAPI())
            edgeservice = self.getService('edge')
            scrapeservice = self.getService('scrape')
            return FollowersScraper(clients, edgeservice, scrapeservice)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 -m app [recenttweets | info | channel | followers]')
        sys.exit(1)

    smisc = SMISC()
    smisc.setupLogging()

    app = smisc.getProgram(sys.argv[1])
    if app is None:
        logging.error('Invalid application "%s"' % (sys.argv[1]))
    else:
        try:
            app.main()
        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))
