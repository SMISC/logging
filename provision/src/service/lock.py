import logging
import time

logger = logging.getLogger(__name__)

class LockService:
    def __init__(self, rds, key):
        self.rds = rds
        self.lock_key = 'lock_%s' % (key)
        self.block_key = 'block_%s' % (key)
        self.acquired = None

    def acquire(self, expire_time = 3600):
        blocked = self.rds.get(self.block_key)
        rv = self.rds.setnx(self.lock_key, time.time())

        if blocked:
            self.acquired = False
            logger.info('%s manually blocked from running', self.lock_key)
        elif not rv:
            self.acquired = False
            time_started = self.inspect()
            logger.info('%s locked (since %.0f minutes ago).', self.lock_key, (time.time() - time_started) / 60)
        else:
            self.acquired = True
            if expire_time is not None:
                self.rds.expire(self.lock_key, expire_time)
            logger.debug('%s acquired and now locked', self.lock_key)

        return self.acquired

    def get_did_acquire(self):
        return self.acquired

    def inspect(self):
        val = self.rds.get(self.lock_key)
        if val:
            return float(val)
        return None

    def release(self):
        if self.acquired:
            logger.debug('%s released', self.lock_key)
            self.rds.delete(self.lock_key)
        else:
            logger.exception('tried to free a lock what was never locked. silently ignoring....')
