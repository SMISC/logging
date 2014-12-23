import time
import datetime
import tempfile
import logging
import base64
import boto.glacier.exceptions

class Backup:
    RECORD_SEPARATOR = 30
    FIELD_SEPARATOR = 31

    def __init__(self, vault, lockservice, backupservice, edgeservice, userservice, tweetservice, scanservices, page_size):
        self.vault = vault
        self.lockservice = lockservice
        self.backupservice = backupservice
        self.edgeservice = edgeservice
        self.userservice = userservice
        self.tweetservice = tweetservice
        self.scanservices = scanservices
        self.page_size = page_size

    def main(self):
        if not self.lockservice.acquire(None): # there is no expire time
            return

        self._runEdges()

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
        
    def _backupTable(self, get_method, delete_method, ref_start, ref_end, name):
        created_dt = datetime.datetime.fromtimestamp(time.time())
        created = created_dt.strftime('%b %d %Y - %H:%M:%S')

        written_columns = False

        row_number = 0

        with tempfile.NamedTemporaryFile() as fd:
            fp = fd.name
            t = 0
            cursor = get_method(ref_start, ref_end)

            for row in cursor:
                if row_number is 0:
                    self._writeHeader(fd, row)

                self._writeRow(fd, row)
                row_number += 1

                if time.time() > t:
                    logging.info('backing up %s - row %d', name, row_number)
                    t = time.time() + 10
                    fd.flush()

            if row_number > 0:
                logging.info('backing up for %s scan [%d, %d) with %d observed refs', name, ref_start, ref_end, row_number)
                            
                try:
                    archive_id = self.vault.upload_archive(fp, 'Snapshot of scan %s %s records [%s, %s)' % (name, created, ref_start, ref_end))
                    logging.info('wrote archive %s' % (archive_id,))
                    self.backupservice.backed_up(name, ref_start, ref_end, archive_id)
                    delete_method(ref_start, ref_end)
                    return
                except boto.glacier.exceptions.UnexpectedHTTPResponseError as e:
                    logging.warn('Ignoring HTTP error %s', str(e))
                    return

        logging.info('not backing up empty scan')

    def _runEdges(self):
        ival = self.backupservice.get_ref_interval('tuser_tuser', self.page_size)

        if ival is not None:
            (min_id, max_id) = ival
            getter = getattr(self.edgeservice, 'get_edges_between')
            deleter = getattr(self.edgeservice, 'delete_between')
            self._backupTable(getter, deleter, min_id, max_id, 'followers')
