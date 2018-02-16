import os
import logging
from . import utils

logger = logging.getLogger(__name__)

HANDLER_ALIASES = {
    'FILE': 'cachely.backends.fs.CacheFileHandler',
    'DB': 'cachely.backends.sqlite.CacheDbHandler'

}

def cachely(handler=None, **params):
    if not handler:
        handler = os.environ.get('CACHELY_HANDLER', 'FILE')

    if isinstance(handler, str):
        handler = HANDLER_ALIASES.get(handler, handler)
        handler = utils.import_string(handler)

    return handler(**params)
