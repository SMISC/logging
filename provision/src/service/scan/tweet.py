from .base import BaseScanService

class TweetScanService(BaseScanService):
    def _get_most_recent_id(self):
        self.db.execute('SELECT MAX(id) from tweet')
        if self.db.rowcount > 0:
            result = self.db.fetchone()
            if result is not None:
                (most_recent_ref_id,) = result
                return most_recent_ref_id
        
        
