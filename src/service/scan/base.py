import time

class BaseScanService:
    def __init__(self, db, typename):
        self.db = db
        self.typename = typename

    def begin_anew(self):
        self.db.execute('SELECT MAX(id) FROM "scan" WHERE "type" = %s', (self.typename,))
        result = self.db.fetchone()
        if result is not None:
            (last_scan_id,) = result

        most_recent_ref_id = self._get_most_recent_id()

        if most_recent_ref_id is not None and last_scan_id is not None:
            self.db.execute('UPDATE "scan" SET "end" = %s, "ref_end" = %s WHERE id = %s', (int(time.time()), most_recent_ref_id, last_scan_id))

        self.db.execute('INSERT INTO "scan" ("type", "start", "end", "ref_start", "ref_end") VALUES (%s, %s, %s, %s, %s)', (self.typename, int(time.time()), None, most_recent_ref_id, None))
