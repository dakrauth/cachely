import os
from pathlib import Path
from functools import cache
from collections import namedtuple
from importlib import import_module
from datetime import datetime, timedelta

import platformdirs
from .. import logger

HANDLER_ALIASES = {
    "FILE": "cachely.backends.fs.CacheFileHandler",
    "DB": "cachely.backends.sqlite.CacheDbHandler",
}


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError:
        error_msg = f"{dotted_path} is not a module path"
        logger.debug(error_msg)
        raise ImportError(error_msg)

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        error_msg = 'Module "{}" does not define a "{}" class'.format(module_path, class_name)
        logger.debug(error_msg)
        raise ImportError(error_msg)


def default_cachely_dirname():
    dirname = os.getenv("CACHELY_DIR")
    if dirname:
        return Path(dirname)

    return platformdirs.user_cache_path("cachely")


class CacheHandler:
    class CacheEntry(namedtuple("CacheEntry", "id,name,content,date,size")):
        __slots__ = ()

        def __str__(self):
            return self.content.decode()

    def __init__(self, dirname=None, ttl=None, **kwargs):
        dirname = dirname or default_cachely_dirname()
        self.base_dir = self.absolute_filename(dirname)
        if ttl is None:
            ttl = os.getenv("CACHELY_TTL", None)
        self.ttl = None if ttl is None else timedelta(float(ttl))

    def is_expired(self, dt):
        if self.ttl is None:
            return False

        return datetime.now() > (dt + self.ttl)

    @property
    def name(self):
        return self.__class__.__name__

    def invalidate(self, url):
        raise NotImplementedError("invalidate")

    def listing(self):
        raise NotImplementedError("listing")

    def get(self, url):
        raise NotImplementedError("get")

    def set(self, url, data):
        raise NotImplementedError("set")

    def delete(self, url):
        raise NotImplementedError("delete")

    @classmethod
    def absolute_filename(cls, filename):
        """
        Do all those annoying things to arrive at a real absolute path.
        """
        return Path(os.path.expandvars(filename)).expanduser().absolute()

    @cache
    @staticmethod
    def load(handler, **params):
        if isinstance(handler, str):
            key = handler.upper()
            handler = import_string(HANDLER_ALIASES[key] if key in HANDLER_ALIASES else handler)

        if handler:
            return handler(**params)

        raise RuntimeError("Unspecified backend handler")
