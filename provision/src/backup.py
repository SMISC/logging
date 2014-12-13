import time
import datetime
import tempfile
import logging
import base64
import boto.glacier.exceptions

class Backup:
    RECORD_SEPARATOR = 30
    FIELD_SEPARATOR = 31

    def __init__(self, vault, lockservice, backupservice, edgeservice, userservice, tweetservice, scanservices):
        self.vault = vault
        self.lockservice = lockservice
        self.backupservice = backupservice
        self.edgeservice = edgeservice
        self.userservice = userservice
        self.tweetservice = tweetservice
        self.scanservices = scanservices

    def main(self):
        if not self.lockservice.acquire(None): # there is no expire time
            return

        self._runEdges()
        self._runUsers()
        self._runTweets()

    def _writeHeader(self, fd, row):
        values = []
        for (key, value) in row.items():
            values.append(str(key).encode('utf-8'))

        self._writeRecord(fd, values)

    def _writeRow(self, fd, row):
        values = []
        for (key, value) in row.items():
            if value is not None:
                values.append(str(value).encode('utf-8'))
            else:
                values.append(''.encode('utf-8'))

        self._writeRecord(fd, values)

    def _writeRecord(self, fd, records):
        for value in records:
            fd.write(value)
            fd.write(chr(self.FIELD_SEPARATOR).encode('utf-8'))

        fd.write(chr(self.RECORD_SEPARATOR).encode('utf-8'))
        
    def _backupTable(self, get_method, delete_method, scan, name):
        created_dt = datetime.datetime.fromtimestamp(time.time())
        created = created_dt.strftime('%b %d %Y - %H:%M:%S')
        scan_time_dt = datetime.datetime.fromtimestamp(scan['start'])
        scan_time = scan_time_dt.strftime('%b %d %Y - %H:%M:%S')

        scan_id = scan['id']
        start = scan['ref_start']
        end = scan['ref_end']
        written_columns = False

        row_number = 0

        with tempfile.NamedTemporaryFile() as fd:
            fp = fd.name
            t = 0
            cursor = get_method(start, end)

            for row in cursor:
                if row_number is 0:
                    self._writeHeader(fd, row)

                self._writeRow(fd, row)
                row_number += 1

                if time.time() > t:
                    logging.info('row %d', row_number)
                    t = time.time() + 10
                    fd.flush()

            if row_number > 0:
                logging.info('backing up for %s scan #%d [%d, %d) with %d observed refs', name, scan_id, start, end, row_number)
                            
                try:
                    archive_id = self.vault.upload_archive(fp, 'Snapshot of scan %s #%d at %s (scan at %s)' % (scan['type'], scan_id, created, scan_time))
                    logging.info('wrote archive %s' % (archive_id,))
                    self.backupservice.mark_backed_up(scan_id, row_number, archive_id)
                    delete_method(start, end)
                except boto.glacier.exceptions.UnexpectedHTTPResponseError as e:
                    logging.warn('Ignoring HTTP error %s', str(e))

        logging.info('not backing up empty scan')
        self.backupservice.mark_backed_up(scan_id, 0, None)

    def _runEdges(self):
        scans = self.backupservice.get_scans_not_backedup('followers_wide')
        if len(scans):
            getter = getattr(self.edgeservice, 'get_edges_between')
            deleter = getattr(self.edgeservice, 'delete_between')
            self._backupTable(getter, deleter, scans[0], 'followers')

    def _runTweets(self):
        '''
        scans = self.backupservice.get_scans_not_backedup('tweets')
        if False: #disable for now
            counter = getattr(self.tweetservice, 'get_tweets_between_count')
            getter = getattr(self.tweetservice, 'get_tweets_between')
            deleter = getattr(self.tweetservice, 'delete_between')
            self._backupTable(counter, getter, deleter, scans[0], 'tweets')
        '''

    def _runUsers(self):
        '''
        scans = self.backupservice.get_scans_not_backedup('info')
        if len(scans) and len(scans) > 1: # need at least one 
            counter = getattr(self.userservice, 'get_users_between_count')
            getter = getattr(self.userservice, 'get_users_between')
            deleter = getattr(self.userservice, 'delete_between')
            self._backupTable(counter, getter, deleter, scans[0], 'info')
        '''
