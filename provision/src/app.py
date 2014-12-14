import psycopg2
import psycopg2.extras
import redis
import sys
import logging
import logging.handlers
import configparser
import boto.glacier
import boto.glacier.layer2

from influxdb import InfluxDBClient

from ratelimit import RateLimitedTwitterAPI
from stats import StatsClient

from twitter import twitter_from_credentials
from twitter import SkipException

from backup import Backup
from scoring import Scoring

from service.scrape import ScrapeService
from service.tweet import TweetService
from service.bot import BotService
from service.teamlink import TeamLinkService
from service.user import UserService
from service.edge import EdgeService
from service.edge import EdgeServiceBig
from service.edge import BotEdgeService
from service.lock import LockService
from service.backup import BackupService
from service.score import ScoreService

from service.scan.info import InfoScanService
from service.scan.tweet import TweetScanService
from service.scan.edge import BotEdgeScanService
from service.scan.edge import BotV2EdgeScanService
from service.scan.edge import WideEdgeScanService

from scraper.needsmeta import NeedsMetaScraper
from scraper.channel import ChannelScraper
from scraper.info import InfoScraper
from scraper.followers import BotFollowersScraper
from scraper.followers import WideFollowersScraper
from scraper.competitiontweets import CompetitionTweetsScraper

class SMISC:
    def __init__(self, app):
        self.app = app
        self.config = configparser.ConfigParser()
        self.config.read('/usr/local/share/smisc.ini')
        self.log = logging.getLogger(None)
        self.rds = None
        self.dbc_auto = None
        self.dbc_noauto = None
        self.locks = []

    def getStats(self):
        ifclient = InfluxDBClient('localhost', 8086, self.config['influxdb']['username'], self.config['influxdb']['password'], self.config['influxdb']['database'])
        return StatsClient(ifclient, self.app)

    def setupLogging(self, level):
        handler = logging.handlers.TimedRotatingFileHandler(self.config['smisc']['log'], when='D', backupCount=5)
        formatter = logging.Formatter('{asctime}\t{name}\t{levelname}\tp{process}\t\t{message}', style='{')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        stdout_handler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(stdout_handler)

        self.log.setLevel(level)

        logging.getLogger('requests').setLevel(logging.ERROR)
        logging.getLogger('boto').setLevel(logging.ERROR)

    def getConfig(self):
        return self.config

    def getRedis(self):
        if self.rds is None:
            self.rds = redis.StrictRedis(host=self.config['redis']['host'], port=self.config['redis']['port'], db=int(self.config['redis']['database']), decode_responses=True)
        return self.rds
        
    def getDatabase(self, autocommit = True):
        if autocommit:
            if self.dbc_auto is None:
                self.dbc_auto = psycopg2.connect(user=self.config['postgres']['username'], password=self.config['postgres']['password'], database=self.config['postgres']['database'], host=self.config['postgres']['host'])
                self.dbc_auto.autocommit = True
            return self.dbc_auto
        else:
            if self.dbc_noauto is None:
                self.dbc_noauto = psycopg2.connect(user=self.config['postgres']['username'], password=self.config['postgres']['password'], database=self.config['postgres']['database'], host=self.config['postgres']['host'])
            return self.dbc_noauto
        
    def getDatabaseCursor(self, name = None, autocommit = True):
        dbc = self.getDatabase(autocommit)
        return dbc.cursor(name = name, cursor_factory=psycopg2.extras.DictCursor)
    
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

        return RateLimitedTwitterAPI(apis, self.getStats())

    def getService(self, which, *args):
        if 'tweet' == which:
            return TweetService(self.getDatabaseCursor())
        elif 'user' == which:
            return UserService(self.getDatabaseCursor())
        elif 'scrape' == which:
            return ScrapeService(self.getRedis(), args[0])
        elif 'edge' == which:
            return EdgeService(self.getDatabaseCursor())
        elif 'bot_edge' == which:
            return BotEdgeService(self.getDatabaseCursor())
        elif 'backup' == which:
            return BackupService(self.getDatabaseCursor())
        elif 'bot' == which:
            return BotService(self.getDatabaseCursor())
        elif 'teamlink' == which:
            return TeamLinkService(self.getDatabaseCursor())
        elif 'score' == which:
            return ScoreService(self.getDatabaseCursor())
        elif 'scan' == which:
            backend = args[0]
            if 'info' == backend:
                return InfoScanService(self.getDatabaseCursor(), backend)
            elif 'tweets' == backend:
                return TweetScanService(self.getDatabaseCursor(), backend)
            elif 'followers_wide' == backend or 'followers' == backend:
                return WideEdgeScanService(self.getDatabaseCursor(), backend)
            elif 'followers_bot' == backend:
                return BotEdgeScanService(self.getDatabaseCursor(), backend)
            elif 'followers_bot_v2' == backend:
                return BotV2EdgeScanService(self.getDatabaseCursor(), backend)

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

        elif 'followers_wide' == which:
            clients = []
            edgeservices = []
            scrapeservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(32):
                clients.append(self.getTwitterAPI())
                edgeservices.append(self.getService('edge'))
                scrapeservices.append(self.getService('scrape', 'followers_wide'))

            scrapeservices.append(self.getService('scrape', 'followers_wide')) # append an extra for main thread 

            scanservice = self.getService('scan', 'followers_wide')

            return WideFollowersScraper(clients, edgeservices, userservice, lockservice, scrapeservices, scanservice)

        elif 'followers_bot' == which:
            clients = []
            edgeservices = []
            scrapeservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)
            for i in range(32):
                clients.append(self.getTwitterAPI())
                edgeservices.append(self.getService('edge'))
                scrapeservices.append(self.getService('scrape', 'followers_bot'))

            scrapeservices.append(self.getService('scrape', 'followers_bot')) # append an extra for main thread 

            scanservice = self.getService('scan', 'followers_bot')

            return BotFollowersScraper(clients, edgeservices, userservice, lockservice, scrapeservices, scanservice)

        elif 'followers_bot_v2' == which:
            clients = []
            edgeservices = []
            scrapeservices = []
            botservices = []
            userservice = self.getService('user')
            lockservice = self.getService('lock', which)

            for i in range(32):
                clients.append(self.getTwitterAPI())
                edgeservices.append(self.getService('bot_edge'))
                botservices.append(self.getService('bot'))
                scrapeservices.append(self.getService('scrape', 'followers_bot_v2'))

            scrapeservices.append(self.getService('scrape', 'followers_bot_v2')) # append an extra for main thread 

            scanservice = self.getService('scan', 'followers_bot_v2')

            return BotFollowersScraper(clients, edgeservices, userservice, lockservice, scrapeservices, scanservice, botservices)

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
            backupservice = self.getService('backup')
            edgeservice = EdgeServiceBig(self.getDatabaseCursor(), self.getDatabaseCursor('backupedge', False))
            userservice = self.getService('user')
            tweetservice = self.getService('tweet')
            scanservices = {
                'followers': self.getService('scan', 'followers'),
                'info': self.getService('scan', 'info'),
                'tweets': self.getService('scan', 'tweets')
            }

            return Backup(vault, lockservice, backupservice, edgeservice, userservice, tweetservice, scanservices)
        
        elif 'scoring' == which:
            lockservice = self.getService('lock', which)
            botservice = self.getService('bot')
            teamlinkservice = self.getService('teamlink')
            tweetservice = self.getService('tweet')
            scoreservice = self.getService('score')
            return Scoring(lockservice, botservice, teamlinkservice, tweetservice, scoreservice)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 -m app [channel | followers | competition-tweets]')
        sys.exit(1)

    app_name = sys.argv[1]

    smisc = SMISC(app_name)
    smisc.setupLogging(logging.DEBUG)

    app = smisc.getProgram(app_name)
    stats = smisc.getStats()

    if app is None:
        logging.error('Invalid application "%s"' % (app_name))
    else:
        try:
            app.main()
            logging.debug('%s completed successfully.', app_name)
            stats.log_app_return(0)
        except Exception as err:
            logging.exception('Caught error: %s' % (str(err)))
            stats.log_app_return(1)
        finally:
            for lock in smisc.locks:
                if lock.get_did_acquire():
                    lock.release()
            

