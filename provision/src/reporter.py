import psutil
import os
import time
import logging

class Reporter:
    RUNTIME = 50
    STEP = 20

    def __init__(self, lockservice, stats, queues):
        self.lockservice = lockservice
        self.stats = stats
        self.queues = queues

    def main(self):
        if not self.lockservice.acquire(self.RUNTIME * 2):
            return

        time_start = time.time()

        while time.time() < (time_start + self.RUNTIME):

            logging.info('reporting statistics to InfluxDB')

            self._reportQueueLengths()
            self._reportMachineStatistics()

            self.stats.flush()

            time.sleep(self.STEP)

    def _reportQueueLengths(self):
        for (qn, queue) in self.queues.items():
            self.stats.log_queue_length(qn, queue.length())

    def _reportMachineStatistics(self):
        load = os.getloadavg()
        self.stats.log_loadavg(load[0], load[1], load[2])

        memory = psutil.virtual_memory()
        self.stats.log_memory(memory.free, memory.total)

        du = psutil.disk_usage('/')
        self.stats.log_diskusage(du.free, du.total)
