import os
import atexit
from urllib.parse import urlparse, ParseResult
import logging
from . import utils
from .cache import cachely

logger = logging.getLogger(__name__)


class Loader:
    '''
    A cache loading manager to handle downloading bits from URLs and saving
    them locally.

    TODO: add feature to clear cache / force re-download.
    '''

    def __init__(self, use_cache=True, **cache_params):
        self.use_cache = use_cache
        self.cache_params = cache_params

    @property
    def cache(self):
        return cachely(**self.cache_params) if self.use_cache else None

    def load_sources(self, sources):
        return [self.load_source(src) for src in sources]

    def load_source(self, url):
        purl = urlparse(url)
        data = None
        if purl.scheme.lower() in ('file', ''):
            logger.debug('Reading from file: {}'.format(purl.path))
            return utils.read_file(purl.path)

        cache = self.cache

        if cache and cache.exists(url):
            data = cache.read(url)
        else:
            logger.debug('Fetching content from: {}'.format(url))
            data, content_type = utils.read_url(url)
            
            logger.debug('Retrieved {} bytes from {}'.format(len(data), url))
            if self.use_cache:
                cache.write(url, data)

        return data

