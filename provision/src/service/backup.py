import logging
import base64
import time

from model import Model

class BackupService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "backups")

    def get_ref_interval(self, tbl, howmany):
        self.db.execute('select min(id) over (), max(id) over (rows between unbounded preceding and ' + str(howmany) + ' following) from ' + tbl + ' order by id asc limit 1')
        rslt = self.db.fetchone()
        return (rslt[0], rslt[1])

    def backed_up(self, table, ref_start, ref_end, glacier_id, timestamp = None):
        if timestamp is None:
            timestamp = int(time.time())

        self.db.execute('insert into backups ("table", timestamp, ref_start, ref_end, glacier_id) values (%s, %s, %s, %s, %s)', (table, timestamp, ref_start, ref_end, glacier_id))
