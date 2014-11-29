import logging
import base64

class Backup:
    def __init__(self, vault, lockservice, backupservice, edgeservice, userservice, tweetservice, scanservices):
        self.vault = vault
        self.lockservice = lockservice
        self.backupservice = backupservice
        self.edgeservice = edgeservice
        self.userservice = userservice
        self.tweetservice = tweetservice
        self.scanservices = scanservices

    def main(self):
        self._runEdges()
        self._runUsers()
        self._runTweets()

    def _runEdges(self):
        scan_ids = self.backupservice.get_scans_not_backedup('followers')

        for scan_id in scan_ids:
            logging.info('backing up followers scan #%d', scan['id'], scan['ref_start'], scan['ref_end'])

    def _runTweets(self):
        scan_ids = self.backupservice.get_scans_not_backedup('tweets')

        for scan_id in scan_ids:
            logging.info('backing up tweet scan #%d', scan['id'], scan['ref_start'], scan['ref_end'])

    def _runUsers(self):
        scan_ids = self.backupservice.get_scans_not_backedup('info')

        for scan_id in scan_ids:
            logging.info('backing up info scan #%d from %d to %d', scan['id'], scan['ref_start'], scan['ref_ned'])
