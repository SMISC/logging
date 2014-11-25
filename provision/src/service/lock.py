import logging
import time

logger = logging.getLogger(__name__)

class LockService:
    def __init__(self, rds, key):
        self.rds = rds
        self.key = 'lock_%s' % (key)
        self.acquired = None

    def acquire(self):
        rv = self.rds.setnx(self.key, time.time())
        self.acquired = rv

        if not rv:
            time_started = self.inspect()
            logger.info('%s locked (since %.0f minutes ago).', self.key, (time.time() - time_started) / 60)
        else:
            self.rds.expire(self.key, 360)
            logger.debug('%s acquired and now locked', self.key)

        return rv

    def get_did_acquire(self):
        return self.acquired

    def inspect(self):
        val = self.rds.get(self.key)
        if val:
            return float(val)
        return None

    def release(self):
        if self.acquired:
            logger.debug('%s released', self.key)
            self.rds.delete(self.key)
        else:
            logger.exception('tried to free a lock what was never locked. silently ignoring....')
