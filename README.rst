=======
Cachely
=======

A very simplistic resource caching utility for retrieving and storing
web content locally to either the file system or SQLite database.

API
===

::

    from cachely.client import Client
    client = Client()
    content = client.load_content("https://example.com")

CLI
===

::

    $ cachely --help
    usage: cachely [-h] [--list] [--delete] [--purge] [--ttl TTL] [--dirname DIRNAME] [--filename FILENAME] [--backend BACKEND] [--info] [--verbose] [URL]

    positional arguments:
      URL

    options:
      -h, --help            show this help message and exit
      --list, -l            Show a listing of cached URLs.
      --delete              Delete the entry for a given URL or ID.
      --purge               Purge all cached entries.
      --ttl TTL, -t TTL     Set the time-to-live value in days for a new entry.
      --dirname DIRNAME, -d DIRNAME
                            Directory location to use for database/files.
      --filename FILENAME, -f FILENAME
                            Filename to use for sqlite database, if used.
      --backend BACKEND, -b BACKEND
                            Specify cache storage: FILE, DB, or python import string for backend
      --info                Show cache info and exit.
      --verbose, -v         Toggle debug output.
