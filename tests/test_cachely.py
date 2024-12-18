from pathlib import Path
import sqlite3

import pytest
import responses
from cachely.client import Client

HERE = Path(__file__).parent


@pytest.fixture(scope="function")
def db_client():
    client = Client(dirname=HERE)
    yield client

    client.backend.filename.unlink()


def test_db(db_client):
    assert not db_client.backend.filename.exists(), "Database file should not exist"

    with responses.RequestsMock() as rsp:
        base = "https://example.com/"
        for i in range(1, 4):
            url = f"{base}{i}"
            rsp.add(responses.GET, url, body=b"Hello, world", status=200)
            content = db_client.load_content(url)
            assert content == b"Hello, world"

    db = sqlite3.connect(db_client.backend.filename)
    row = db.execute("SELECT COUNT(*) from `cachely`").fetchone()
    assert row[0] == 3


def test_file():
    client = Client(backend="file", dirname=HERE)
    with responses.RequestsMock() as rsp:
        url = "https://example.com"
        rsp.add(responses.GET, url, body=b"Hello, world", status=200)
        content = client.load_content(url)
        assert content == b"Hello, world"

    filepath = HERE / "https%3A%2F%2Fexample.com"
    assert filepath.exists()
    filepath.unlink()
