import os
import logging
import sqlite3
from datetime import datetime

from .. import utils
from .base import CacheBaseHandler, CacheEntry

logger = logging.getLogger(__name__)


class CacheDbHandler(CacheBaseHandler):

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.filename = os.path.join(
            self.base_dir,
            kws.get('filename', os.environ.get('CACHELY_DBNAME', 'cachely.db'))
        )

    @property
    def db(self):
        db = sqlite3.connect(self.filename)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS `cachely` (
                `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `name`  TEXT NOT NULL,
                `date`  INTEGER NOT NULL,
                `content`   BLOB NOT NULL
            )
        ''')

        return db

    def listing(self):
        return [
            CacheEntry(name, len(content), datetime.fromtimestamp(date))
            for name, content, date in self.db.cursor().execute('''
                SELECT `name`, `content`, `date`
                FROM `cachely`
                ORDER BY `date`
            ''')
        ]


    def exists(self, url):
        row = self.db.cursor().execute(
            '''SELECT COUNT(`name`) FROM `cachely` WHERE `name` = ?''',
            (url,)
        ).fetchone()
        return bool(row[0])

    def read(self, url):
        row = self.db.cursor().execute(
            '''SELECT `content` FROM `cachely` WHERE `name` = ?''',
            (url,)
        ).fetchone()
        if row:
            return row[0].decode()


    def write(self, url, data):
        db = self.db
        db.cursor().execute(
            '''INSERT INTO `cachely` VALUES (NULL, ?, ?, ?)''',
            (url, int(datetime.now().timestamp()), data)
        )
        db.commit()
        db.close()

