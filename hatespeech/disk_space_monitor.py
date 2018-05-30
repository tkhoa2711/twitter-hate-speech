from shutil import disk_usage
from hatespeech.config import config
from hatespeech.api.database import clean_old_data
from hatespeech.api.logging2 import log
from hatespeech.api.utils import StoppableThread, start_thread


class _MonitorDiskUsageThread(StoppableThread):
    def run(self):
        interval = 60   # seconds
        while not self.is_stopped():
            try:
                usage = disk_usage('.')
                free = usage.free / usage.total * 100.0
                log.debug(f"Disk usage [{free}% free]: {usage}")

                threshold = config.DISK_FREE_THRESHOLD
                if free < threshold:
                    log.warn(f"Disk space left {free:.2f}% is below threshold of {threshold:.2f}%")
                    clean_old_data()
            except Exception:
                log.exception("Error during disk usage monitoring")
            finally:
                if self.is_stopped():
                    return
                self.sleep(interval)


def monitor_disk_usage():
    """
    Start monitoring disk usage in a separate thread.
    """
    start_thread(_MonitorDiskUsageThread())
    log.info("Started monitoring disk usage")

