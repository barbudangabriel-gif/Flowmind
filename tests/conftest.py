import os

os.environ.setdefault("TEST_MODE", "1")  # all Redis goes in-memory for tests

import sqlite3
import tempfile
import pytest
from fastapi.testclient import TestClient

# App principal
import sys

# sys.path.append("/app/backend")
# from server import app


@pytest.fixture(scope="session")
def test_db_path():
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tf.close()
    yield tf.name
    try:
        os.unlink(tf.name)
    except Exception:
        pass


@pytest.fixture(scope="session")
def test_db(test_db_path):
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    # DDL minimal – păstrează sincron cu aplicația
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS portfolios (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          cash_balance REAL NOT NULL DEFAULT 50000.0,
          status TEXT NOT NULL DEFAULT 'ACTIVE',
          modules TEXT,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS marks (
          symbol TEXT PRIMARY KEY,
          last REAL,
          today_open REAL,
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS oauth_tokens (
          provider TEXT PRIMARY KEY,
          access_token TEXT NOT NULL,
          refresh_token TEXT,
          expires_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS eod_snapshots (
          id TEXT PRIMARY KEY,
          portfolio_id TEXT NOT NULL,
          date TEXT NOT NULL,
          realized REAL NOT NULL,
          unrealized REAL NOT NULL,
          total REAL NOT NULL,
          cash_balance REAL,
          positions_count INTEGER,
          timestamp TEXT,
          timezone TEXT DEFAULT 'Europe/Bucharest',
          UNIQUE(portfolio_id, date)
        );
        """
    )
    # Seed minimal
    conn.execute(
        "INSERT INTO portfolios(id, name) VALUES('pf_test123', 'Test Portfolio')"
    )
    # mark current pentru TSLA
    conn.execute(
        "INSERT INTO marks(symbol,last,today_open) VALUES(?,?,?)",
        ("TSLA", 245.6, 240.1),
    )
    conn.commit()
    return conn


# Database override not needed since app doesn't use get_db dependency


@pytest.fixture
def client():
    return TestClient(app)
