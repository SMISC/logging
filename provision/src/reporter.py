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

        nio = None

        while time.time() < (time_start + self.RUNTIME):

            logging.info('reporting statistics to InfluxDB')

            self._reportQueueLengths()
            nio = self._reportMachineStatistics(nio)

            self.stats.flush()

            time.sleep(self.STEP)

    def _reportQueueLengths(self):
        for (qn, queue) in self.queues.items():
            self.stats.log_queue_length(qn, queue.length())

    def _reportMachineStatistics(self, prev_nio):
        load = os.getloadavg()
        self.stats.log_loadavg(load[0], load[1], load[2])

        memory = psutil.virtual_memory()
        self.stats.log_memory(memory.free, memory.total)

        du = psutil.disk_usage('/')
        self.stats.log_diskusage(du.free, du.total)

        cur_nio = psutil.net_io_counters()

        if prev_nio is not None:
            self.stats.log_throughput(cur_nio.bytes_sent - prev_nio.bytes_sent, cur_nio.bytes_recv - prev_nio.bytes_recv)

        return cur_nio
