import itertools

class ScanService:
    def __init__(self, db):
        self.db = db
        self.cur_scan = None
    def new_scan(self, now, max_breadth):
        self.db.execute('INSERT INTO "scan" (start_time, end_time) VALUES(%s, NULL);', (now,))
        self.db.execute('SELECT currval(\'scan_id_seq\');')
        scan_id = self.db.fetchone()[0]
        self.cur_scan = Scan(scan_id, max_breadth)
        return self.cur_scan
    def done(self, now):
        self.db.execute('UPDATE "scan" SET end_time = %s WHERE id = %s', (now, self.cur_scan.getId()))
        self.cur_scan = None

class Scan:
    def __init__(self, scan_id, max_breadth):
        self.scan_id = scan_id
        self.max_breadth = max_breadth
    def getId(self):
        return self.scan_id
    def getMaxBreadth(self):
        return self.max_breadth
