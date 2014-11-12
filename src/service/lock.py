import time

class LockService:
    def __init__(self, rds):
        self.rds = rds

    def _getKey(self, what):
        return 'lock_%s' % (what)

    def acquire(self, what):
        return self.rds.setnx(self._getKey(what), time.time())

    def inspect(self, what):
        val = self.rds.get(self._getKey(what))
        if val:
            return float(val)
        return None

    def release(self, what):
        self.rds.delete(self._getKey(what))
