import os
import time
import logging

from sdap_ingest_manager.config.exceptions import UnreadableFileException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

LISTEN_FOR_UPDATE_INTERVAL_SECONDS = 1


class LocalDirConfig:
    def __init__(self, local_dir):
        self._local_dir = local_dir
        self._latest_update = self._get_latest_update()
        
    def get_files(self):
        files = []
        for f in os.listdir(self._local_dir):
            if os.path.isfile(os.path.join(self._local_dir, f)) \
                    and 'README' not in f \
                    and not f.startswith('.'):
                files.append(f)

        return files

    def get_file_content(self, file_name):
        logger.info(f'read configuration file {file_name}')
        try:
            with open(os.path.join(self._local_dir, file_name)) as f:
                    return f.read()
        except UnicodeDecodeError as e:
            raise UnreadableFileException(e)

    def _get_latest_update(self):
        return time.ctime(max(os.path.getmtime(root) for root,_,_ in os.walk(self._local_dir)))

    def when_updated(self, callback):
        while True:
            time.sleep(LISTEN_FOR_UPDATE_INTERVAL_SECONDS)
            latest_update = self._get_latest_update()
            if latest_update > self._latest_update:
                logger.info("local config dir has been updated")
                callback()
                self._latest_update = latest_update
            else:
                logger.debug("local config dir has not been updated")
