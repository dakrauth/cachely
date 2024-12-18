import random

import requests

from . import logger
from .backends.base import CacheHandler


USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",  # noqa
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",  # noqa
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",  # noqa
)


class Client:
    """
    A cache loading manager to handle downloading bits from URLs and saving
    them locally.
    """

    def __init__(self, backend="DB", **cache_params):
        if isinstance(backend, str):
            backend = CacheHandler.load(backend, **cache_params)

        self.backend = backend

    def delete_content(self, url):
        self.backend.delete(url)

    @staticmethod
    def read_url(url, user_agent="random", extra_headers=None):
        """
        A very simplified get request to the given ``url``.
        """
        headers = {"accept-language": "en-US,en"}
        if user_agent:
            headers["User-Agent"] = (
                random.choice(USER_AGENTS) if user_agent == "random" else user_agent
            )

        if extra_headers:
            headers.update(extra_headers)

        r = requests.get(url, headers=headers)
        if not r.ok:
            raise requests.HTTPError("URL {}: {}".format(r.reason, url))

        return r.content

    def load_content(self, url):
        e = self.backend.invalidate(url)
        if e:
            return e.content

        logger.debug(f"Fetching content from: {url}")
        data = self.read_url(url)

        logger.debug(f"Retrieved {len(data)} bytes")
        return self.backend.set(url, data)
