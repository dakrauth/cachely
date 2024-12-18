import os
import sqlite3
import contextlib
from datetime import datetime

from .base import CacheHandler

LIST = "SELECT `id`, `name`, `content`, `date` FROM `cachely` ORDER BY `date`"
EXISTS = "SELECT exists(SELECT 1 FROM `cachely` WHERE `name`=?) as it_exists"
READ = "SELECT `id`, `name`, `content`, `date` FROM `cachely` WHERE `name` = ?"
WRITE = "INSERT INTO `cachely` VALUES (NULL, ?, ?, ?)"
DELETE_BY_NAME = "DELETE FROM `cachely` where `name`=?"
DELETE_BY_ID = "DELETE FROM `cachely` where `id`=?"
CREATE = """
    CREATE TABLE IF NOT EXISTS `cachely` (
        `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `name`  TEXT NOT NULL,
        `content`   BLOB NOT NULL,
        `date`  INTEGER NOT NULL
    )"""


class CacheDbHandler(CacheHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filename = kwargs.get("filename") or os.getenv("CACHELY_DBNAME", "cachely.db")
        self.filename = self.base_dir / filename

    @contextlib.contextmanager
    def db(self, commit=False):
        exists = self.filename.exists()
        parent = self.filename.parent
        if not parent.exists():
            parent.mkdir(parents=True)

        db = sqlite3.connect(self.filename)
        if not exists:
            cursor = db.cursor()
            cursor.execute(CREATE)
            db.commit()
        try:
            yield db
        finally:
            if commit:
                db.commit()

            db.close()

    def invalidate(self, url):
        e = None
        with self.db() as db:
            row = db.execute(READ, (url,)).fetchone()
            if row:
                e = self._cache_entry(row)
                if self.is_expired(e.date):
                    self.delete(url)
                    e = None

        return e

    def _cache_entry(self, row):
        id, name, content, date = row
        return self.CacheEntry(id, name, content, datetime.fromtimestamp(date), len(content))

    def listing(self):
        with self.db() as db:
            return [self._cache_entry(row) for row in db.execute(LIST)]

    def get(self, url):
        e = self.invalidate(url)
        return e.content if e else None

    def set(self, url, data):
        with self.db(commit=True) as db:
            db.cursor().execute(WRITE, (url, data, int(datetime.now().timestamp())))

        return data

    def delete(self, url):
        sql = DELETE_BY_ID if url.isdigit() else DELETE_BY_NAME
        with self.db(commit=True) as db:
            db.cursor().execute(sql, (url,))
