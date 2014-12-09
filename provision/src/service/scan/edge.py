from .base import BaseScanService

class EdgeScanService(BaseScanService):
    def _get_most_recent_id(self):
        self.db.execute('SELECT MAX(id) from tuser_tuser WHERE ' + self._get_where())
        if self.db.rowcount > 0:
            result = self.db.fetchone()
            if result is not None:
                (most_recent_ref_id,) = result
                return most_recent_ref_id
        
        
class BotEdgeScanService(EdgeScanService):
    def _get_where(self):
        return 'bot = TRUE'

class WideEdgeScanService(EdgeScanService):
    def _get_where(self):
        return '1=1'

class BotV2EdgeScanService(BaseScanService):
    def _get_most_recent_id(self):
        self.db.execute('SELECT MAX(id) from tuser_tuser_bot')
        if self.db.rowcount > 0:
            result = self.db.fetchone()
            if result is not None:
                (most_recent_ref_id,) = result
                return most_recent_ref_id
