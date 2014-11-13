import logging
import time

class LockService:
    def __init__(self, rds, expire_time = 3600):
        self.rds = rds
        self.expire_time = expire_time

    def _getKey(self, what):
        return 'lock_%s' % (what)

    def acquire(self, what):
        rv = self.rds.execute_command('SET %s %d EX %d NX' % (self._getKey(what), int(time.time()), self.expire_time))

        if not rv:
            time_started = self.inspect(what)
            logging.info('%s locked (since %.0f minutes ago).', what, (time.time() - time_started) / 60)
        else:
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
