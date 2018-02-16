import os
import logging
from datetime import datetime, timedelta
from collections import namedtuple

from .. import utils

logger = logging.getLogger(__name__)


class CacheBaseHandler:

    def __init__(self, cachely_dirname=None, **params):
        cachely_dirname = cachely_dirname or utils.default_cachely_dirname()
        self.base_dir=utils.absolute_filename(cachely_dirname)
        self.ttl = params.get('ttl', None) or timedelta(days=7)

    @property
    def name(self):
        return self.__class__.__name__

    def listing(self):
        raise NotImplementedError('write')

    def exists(self, url):
        raise NotImplementedError('__bool__')

    def read(self, url):
        raise NotImplementedError('read')

    def write(self, url, data):
        raise NotImplementedError('write')


class CacheEntry(namedtuple('CacheEntry', 'name,size,date')):
    __slots__ = ()

    @classmethod
    def from_filename(cls, filename):
        st = os.stat(filename)
        date = datetime.fromtimestamp(st.st_mtime)
        return cls(filename, st.st_size, date)

