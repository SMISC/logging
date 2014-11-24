import base64

class BackupService:
    def __init__(self, glacier, db, edgeservice, userservice, tweetservice):
        self.glacier = glacier
        self.db = db
        self.scanservice = scanservice
        self.edgeservice = edgeservice
        self.userservice = userservice
        self.tweetservice = tweetservice

    def run(self):
        self._runEdges()
        self._runUsers()
        self._runTweets()

    def _runEdges(self):
        pass

    def _runTweets(self):
        pass

    def _runUsers(self):
        pass
