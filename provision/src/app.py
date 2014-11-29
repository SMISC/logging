import psycopg2
import psycopg2.extras
import redis
import sys
import logging
import logging.handlers
import configparser
import boto.glacier
import boto.glacier.layer2

from ratelimit import RateLimitedTwitterAPI

from twitter import twitter_from_credentials
from twitter import SkipException

from backup import Backup

from service.scrape import ScrapeService
from service.tweet import TweetService
from service.user import UserService
from service.edge import EdgeService
from service.lock import LockService
from service.backup import BackupService

from service.scan.info import InfoScanService
from service.scan.tweet import TweetScanService
from service.scan.edge import EdgeScanService

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
        handler = logging.handlers.TimedRotatingFileHandler(self.config['smisc']['log'], when='D', backupCount=5)
        formatter = logging.Formatter('{asctime}\t{name}\t{levelname}\tp{process}\t\t{message}', style='{')
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
            self.rds = redis.StrictRedis(host=self.config['redis']['host'], port=self.config['redis']['port'], db=int(self.config['redis']['database']), decode_responses=True)
        return self.rds
        
    def getDatabase(self):
        if self.dbc is None:
            self.dbc = psycopg2.connect(user=self.config['postgres']['username'], password=self.config['postgres']['password'], database=self.config['postgres']['database'], host=self.config['postgres']['host'])
            self.dbc.autocommit = True
        return self.dbc
        
    def getDatabaseCursor(self):
        dbc = self.getDatabase()
        return dbc.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    def getTwitterAPI(self):
        keys = self.config['twitter']['keys'].split("\n")
        secrets = self.config['twitter']['secrets'].split("\n")

        apis = []

        for i in range(len(keys)):
            key = keys[i]
            secret = secrets[i]
            try:
                api = twitter_from_credentials(key, secret, self.getRedis())
                apis.append(api)
            except SkipException:
                continue

        return RateLimitedTwitterAPI(apis)

    def getService(self, which, *args):
        if 'tweet' == which:
            return TweetService(self.getDatabaseCursor())
        elif 'user' == which:
            return UserService(self.getDatabaseCursor())
        elif 'scrape' == which:
            return ScrapeService(self.getRedis(), args[0])
        elif 'edge' == which:
            return EdgeService(self.getDatabaseCursor())
        elif 'backup' == which:
            return BackupService(self.getDatabaseCursor())
        elif 'scan' == which:
            backend = args[0]
            if 'info' == backend:
                return InfoScanService(self.getDatabaseCursor(), backend)
            elif 'tweets' == backend:
                return TweetScanService(self.getDatabaseCursor(), backend)
            elif 'followers' == backend:
                return EdgeScanService(self.getDatabaseCursor(), backend)

            raise Exception("Backend for %s not found" % (backend,))

        elif 'lock' == which:
            service = LockService(self.getRedis(), args[0])
            self.locks.append(service)
            return service

    def getProgram(self, which):
        if 'info' == which:
            clients = []
            scrapeservices = []
            userservices = []
            myuserservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(15):
                clients.append(self.getTwitterAPI())
                userservices.append(self.getService('user'))
                scrapeservices.append(self.getService('scrape', 'info'))

            scrapeservices.append(self.getService('scrape', 'info')) # append an extra for main thread 

            scanservice = self.getService('scan', 'info')

            return InfoScraper(clients, userservices, myuserservice, lockservice, scrapeservices, scanservice)

        elif 'followers' == which:
            clients = []
            edgeservices = []
            scrapeservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(32):
                clients.append(self.getTwitterAPI())
                edgeservices.append(self.getService('edge'))
                scrapeservices.append(self.getService('scrape', 'followers'))

            scrapeservices.append(self.getService('scrape', 'followers')) # append an extra for main thread 

            scanservice = self.getService('scan', 'followers')

            return FollowersScraper(clients, edgeservices, userservice, lockservice, scrapeservices, scanservice)

        elif 'competition-tweets' == which:
            clients = []
            tweetservices = []
            scrapeservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(32):
                clients.append(self.getTwitterAPI())
                tweetservices.append(self.getService('tweet'))
                scrapeservices.append(self.getService('scrape', 'tweets'))

            scrapeservices.append(self.getService('scrape', 'tweets')) # append an extra for main thread 

            scanservice = self.getService('scan', 'tweets')

            return CompetitionTweetsScraper(clients, tweetservices, userservice, lockservice, scrapeservices, scanservice)

        elif 'backup' == which:
            glacier = boto.glacier.layer2.Layer2(self.config.get('glacier', 'key'), self.config.get('glacier', 'secret'), region_name=self.config.get('glacier', 'region'))
            vault = glacier.get_vault(self.config.get('glacier', 'vault-postgresqlbackups'))
            lockservice = self.getService('lock', which)
            backupservices = self.getService('backup')
            edgeservice = self.getService('edge')
            userservice = self.getService('user')
            scanservices = {
                'followers': self.getService('scan', 'followers'),
                'info': self.getService('scan', 'info'),
                'tweets': self.getService('scan', 'tweets')
            }

            return Backup(vault, lockservice, backupservice, edgeservice, userservice, tweetservice, scanservices)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 -m app [channel | followers | competition-tweets]')
        sys.exit(1)

    app_name = sys.argv[1]

    smisc = SMISC(app_name)
    smisc.setupLogging(logging.DEBUG)

    app = smisc.getProgram(app_name)
    if app is None:
        logging.error('Invalid application "%s"' % (app_name))
    else:
        try:
            app.main()
            logging.debug('%s completed successfully.', app_name)
        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))
        finally:
            for lock in smisc.locks:
                if lock.get_did_acquire():
                    lock.release()
            

