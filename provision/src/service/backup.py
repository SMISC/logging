import base64
import time

from model import Model

class BackupService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "backups")

    def get_scans_not_backedup(self, dtype, limit = 1):
        self.db.execute("select * from scan where type = %s and ref_end is not NULL and not exists (select * from backups where backups.scan_id = scan.id) limit %s", (dtype, limit))
        scans = []
        for scan in self._fetch_all():
            if scan['ref_start'] is None:
                scan['ref_start'] = 0
            else:
                scan['ref_start'] = int(scan['ref_start'])
            scan['ref_end'] = int(scan['ref_end'])
            scans.append(scan)

        return scans

    def mark_backed_up(self, scan_id, ref_count, timestamp = None):
        if timestamp is None:
            timestamp = int(time.time())

        self.db.execute('insert into backups (scan_id, timestamp, ref_count) values (%s, %s, %s)', (scan_id, timestamp, ref_count))
