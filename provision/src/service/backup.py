import base64
from model import Model

class BackupService(Model):
    def __init__(self, db):
        Model.__init__(self, db, "backups")

    def get_scans_not_backedup(self, dtype):
        self.db.execute("select * from scan where type = %s and not exists (select * from backups where backups.scan_id = scan.id)", (dtype,))
        return self._fetch_all()
