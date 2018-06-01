from shutil import disk_usage
from hatespeech.config import config
from hatespeech.api.database import clean_old_data, force_clean_old_tweets
from hatespeech.api.logging2 import log
from hatespeech.api.utils import StoppableThread, start_thread


class _MonitorDiskUsageThread(StoppableThread):
    def run(self):
        interval = 60   # seconds
        while not self.is_stopped():
            try:
                free = _get_free_space()
                log.info(f"Disk usage: {free}% free")

                threshold = config.DISK_FREE_THRESHOLD
                if free < threshold:
                    log.warn(f"Disk space left {free:.2f}% is below threshold of {threshold:.2f}%")
                    clean_old_data(days=7)

                    free = _get_free_space()
                    while free < threshold:
                        log.warn(f"Disk space left {free:.2f}% is below threshold of {threshold:.2f}%")
                        force_clean_old_tweets(count=1000)
                        free = _get_free_space()

                    log.info(f"Finished cleaning disk space [{free}% free]")
            except Exception:
                log.exception("Error during disk usage monitoring")
            finally:
                if self.is_stopped():
                    return
                self.sleep(interval)


def _get_free_space():
    """
    Get free disk space in percentage.
    """
    usage = disk_usage('.')
    return usage.free / usage.total * 100.0


def monitor_disk_usage():
    """
    Start monitoring disk usage in a separate thread.
    """
    start_thread(_MonitorDiskUsageThread())
    log.info("Started monitoring disk usage")

