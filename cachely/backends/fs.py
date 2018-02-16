import os
import logging
from datetime import datetime, timedelta
from urllib.parse import quote_plus, unquote_plus

from .. import utils
from .base import CacheBaseHandler, CacheEntry

logger = logging.getLogger(__name__)


class CacheFileHandler(CacheBaseHandler):

    def encoded_filepath(self, url):
        return os.path.join(self.base_dir, quote_plus(url))
    
    def exists(self, url):
        filename = self.encoded_filepath(url)
        if os.path.exists(filename):
            e = CacheEntry.from_filename(filename)
            if e.date < (datetime.now() - self.ttl):
                os.remove(e.name)
            else:
                return True
        return False 

    def read(self, url):
        data = utils.read_file(self.encoded_filepath(url))
        return data.split('\n', 1)[1]

    def write(self, url, data):
        utils.write_file(self.encoded_filepath(url), data)

    def listing(self):
        return [
            CacheEntry.from_filename(e)
            for e in os.listdir(self.base_dir)
            if os.is_file(e) and not e.startswith('.')
        ]
