import logging
import time

class LockService:
    def __init__(self, rds):
        self.rds = rds

    def _getKey(self, what):
        return 'lock_%s' % (what)

    def acquire(self, what):
        rv = self.rds.setnx(self._getKey(what), time.time())

        if not rv:
            time_started = self.inspect(what)
            logging.info('%s locked (since %.0f minutes ago).', what, (time.time() - time_started) / 60)
        else:
            self.rds.expire(self._getKey(what), 3600)
            logging.info('%s acquired and now locked', what)

        return rv

    def inspect(self, what):
        val = self.rds.get(self._getKey(what))
        if val:
            return float(val)
        return None

    def release(self, what):
        logging.debug('%s released', what)
        self.rds.delete(self._getKey(what))
