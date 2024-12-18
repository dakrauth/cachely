import os
from datetime import datetime
from urllib.parse import quote_plus, unquote_plus

from .. import logger
from .base import CacheHandler


class CacheFileHandler(CacheHandler):
    def encoded_filepath(self, url):
        return self.base_dir / quote_plus(url)

    @classmethod
    def cache_entry_from_filename(cls, filename):
        st = os.stat(filename)
        name = unquote_plus(filename.name)
        return cls.CacheEntry(
            st.st_ino,
            name,
            filename.read_bytes(),
            datetime.fromtimestamp(st.st_mtime),
            st.st_size,
        )

    def invalidate(self, url):
        e = None
        filename = self.encoded_filepath(url)
        if filename.exists():
            e = self.cache_entry_from_filename(filename)
            if self.is_expired(e.date):
                filename.unlink()
                e = None

        return e

    def get(self, url):
        e = self.invalidate(url)
        return e.content if e else None

    def set(self, url, data):
        self.write_file(self.encoded_filepath(url), data)
        return data

    def is_cached_file(self, filename):
        return filename.is_file() and "://" in unquote_plus(filename.name)

    def listing(self):
        return [
            self.cache_entry_from_filename(e)
            for e in self.base_dir.iterdir()
            if self.is_cached_file(e)
        ]

    def delete(self, url):
        if url.isdigit():
            raise RuntimeError("TODO: find file by inode number")

        self.encoded_filepath(url).unlink()

    @classmethod
    def write_file(cls, filename, data, encoding="utf8"):
        """
        Write ``data`` to file ``filename``. ``data`` should be bytes, but if data
        is type str, it will be encode using ``encoding``.
        """
        logger.debug(f"Writing file: {filename}")
        filename = cls.absolute_filename(filename)
        parent = filename.parent
        if not parent.exists():
            logger.debug(f"Creating directory {parent}")
            parent.mkdir(parent=True, exist_ok=True)

        if isinstance(data, str):
            data = data.encode(encoding)

        filename.write_bytes(data)
