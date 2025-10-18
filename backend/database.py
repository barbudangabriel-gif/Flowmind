"""
FlowMind Portfolios - Database Layer (SQLite)
Production-ready SQLite database for portfolios, transactions, and analytics
"""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
import os

# Database path
DB_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/flowmind.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class DatabaseManager:
 def __init__(self, db_path: str = DB_PATH):
    self.db_path = db_path
    self.init_database()

 @contextmanager
 def get_connection(self):
    """Get database connection with proper cleanup"""
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()

 def init_database(self):
    """Initialize database with complete schema"""
    with self.get_connection() as conn:
        # Enable foreign keys and WAL mode
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        # Execute complete DDL
        conn.executescript("""
 -- PORTFOLIOS
 CREATE TABLE IF NOT EXISTS portfolios (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 base_currency TEXT NOT NULL DEFAULT 'USD',
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
 );

 -- ACCOUNTS
 CREATE TABLE IF NOT EXISTS accounts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 portfolio_id INTEGER NOT NULL,
 name TEXT NOT NULL,
 broker TEXT,
 currency TEXT NOT NULL DEFAULT 'USD',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
 );
 CREATE INDEX IF NOT EXISTS idx_accounts_portfolio ON accounts(portfolio_id);

 -- TRANSACTIONS
 CREATE TABLE IF NOT EXISTS transactions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 account_id INTEGER NOT NULL,
 datetime TEXT NOT NULL,
 symbol TEXT NOT NULL,
 side TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
 qty REAL NOT NULL,
 price REAL NOT NULL,
 fee REAL NOT NULL DEFAULT 0,
 currency TEXT NOT NULL DEFAULT 'USD',
 notes TEXT,
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 FOREIGN KEY (account_id) REFERENCES accounts(id)
 );
 CREATE INDEX IF NOT EXISTS idx_tx_account ON transactions(account_id);
 CREATE INDEX IF NOT EXISTS idx_tx_symbol ON transactions(symbol);
 CREATE INDEX IF NOT EXISTS idx_tx_datetime ON transactions(datetime);

 -- MARKS (live quotes)
 CREATE TABLE IF NOT EXISTS marks (
 symbol TEXT PRIMARY KEY,
 last REAL,
 today_open REAL,
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
 );

 -- OAUTH TOKENS (TradeStation)
 CREATE TABLE IF NOT EXISTS oauth_tokens (
 provider TEXT PRIMARY KEY,
 access_token TEXT NOT NULL,
 refresh_token TEXT,
 expires_at INTEGER NOT NULL
 );

 -- BUCKETS (sub-portfolios)
 CREATE TABLE IF NOT EXISTS buckets (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 portfolio_id INTEGER NOT NULL,
 name TEXT NOT NULL,
 start_value REAL NOT NULL DEFAULT 0,
 notes TEXT,
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
 );

 -- BUCKET RULES
 CREATE TABLE IF NOT EXISTS bucket_rules (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 bucket_id INTEGER NOT NULL,
 symbol_contains TEXT,
 side TEXT CHECK (side IN ('BUY','SELL') OR side IS NULL),
 opt_type TEXT CHECK (opt_type IN ('PUT','CALL') OR opt_type IS NULL),
 account_id INTEGER,
 FOREIGN KEY (bucket_id) REFERENCES buckets(id)
 );
 CREATE INDEX IF NOT EXISTS idx_bucket_rules_bucket ON bucket_rules(bucket_id);
 """)
        conn.commit()

 # Portfolio operations
 def get_portfolios(self) -> List[Dict[str, Any]]:
    """Get all portfolios"""
    with self.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM portfolios ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

 def create_portfolio(self, name: str, base_currency: str = "USD") -> Dict[str, Any]:
    """Create new portfolio"""
    with self.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO portfolios (name, base_currency) VALUES (?, ?)",
            (name, base_currency),
        )
        portfolio_id = cursor.lastrowid
        conn.commit()

        # Return created portfolio
        cursor = conn.execute(
            "SELECT * FROM portfolios WHERE id = ?", (portfolio_id,)
        )
        return dict(cursor.fetchone())

 def get_portfolio(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
    """Get portfolio by ID"""
    with self.get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM portfolios WHERE id = ?", (portfolio_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

 # Account operations
 def get_accounts(self, portfolio_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get accounts, optionally filtered by portfolio"""
    with self.get_connection() as conn:
        if portfolio_id:
            cursor = conn.execute(
                "SELECT * FROM accounts WHERE portfolio_id = ? ORDER BY created_at DESC",
                (portfolio_id,),
            )
        else:
            cursor = conn.execute("SELECT * FROM accounts ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

 def create_account(
    self,
    portfolio_id: int,
    name: str,
    broker: Optional[str] = None,
    currency: str = "USD",
 ) -> Dict[str, Any]:
    """Create new account"""
    with self.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO accounts (portfolio_id, name, broker, currency) VALUES (?, ?, ?, ?)",
            (portfolio_id, name, broker, currency),
        )
        account_id = cursor.lastrowid
        conn.commit()

        cursor = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        return dict(cursor.fetchone())

 # Transaction operations
 def get_transactions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get transactions with filters"""
    query = "SELECT t.* FROM transactions t"
    params = []
    where_clauses = []

    if filters.get("portfolio_id"):
        query += " JOIN accounts a ON a.id = t.account_id"
        where_clauses.append("a.portfolio_id = ?")
        params.append(filters["portfolio_id"])

    if filters.get("account_id"):
        where_clauses.append("t.account_id = ?")
        params.append(filters["account_id"])

    if filters.get("symbol"):
        where_clauses.append("t.symbol = ?")
        params.append(filters["symbol"])

    if filters.get("from"):
        where_clauses.append("t.datetime >= ?")
        params.append(filters["from"])

    if filters.get("to"):
        where_clauses.append("t.datetime <= ?")
        params.append(filters["to"])

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY t.datetime ASC, t.id ASC"

    with self.get_connection() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

 def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new transaction"""
    with self.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO transactions 
            (account_id, datetime, symbol, side, qty, price, fee, currency, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_data["account_id"],
                transaction_data["datetime"],
                transaction_data["symbol"],
                transaction_data["side"],
                transaction_data["qty"],
                transaction_data["price"],
                transaction_data.get("fee", 0),
                transaction_data.get("currency", "USD"),
                transaction_data.get("notes"),
            ),
        )
        transaction_id = cursor.lastrowid
        conn.commit()

        cursor = conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        )
        return dict(cursor.fetchone())

 # Marks operations
 def get_marks(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get market prices"""
    with self.get_connection() as conn:
        if symbol:
            cursor = conn.execute("SELECT * FROM marks WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            return [dict(row)] if row else []
        else:
            cursor = conn.execute("SELECT * FROM marks")
            return [dict(row) for row in cursor.fetchall()]

 def upsert_mark(
    self,
    symbol: str,
    last: Optional[float] = None,
    today_open: Optional[float] = None,
 ):
    """Insert or update market price"""
    with self.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO marks (symbol, last, today_open, updated_at) 
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(symbol) DO UPDATE SET 
            last = COALESCE(excluded.last, last),
            today_open = COALESCE(excluded.today_open, today_open),
            updated_at = datetime('now')
            """,
            (symbol, last, today_open),
        )
        conn.commit()

 # OAuth token operations
 def get_oauth_token(self, provider: str) -> Optional[Dict[str, Any]]:
    """Get OAuth token for provider"""
    with self.get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM oauth_tokens WHERE provider = ?", (provider,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

 def upsert_oauth_token(
    self,
    provider: str,
    access_token: str,
    refresh_token: Optional[str],
    expires_at: int,
 ):
    """Insert or update OAuth token"""
    with self.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO oauth_tokens (provider, access_token, refresh_token, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(provider) DO UPDATE SET
            access_token = excluded.access_token,
            refresh_token = COALESCE(excluded.refresh_token, refresh_token),
            expires_at = excluded.expires_at
            """,
            (provider, access_token, refresh_token, expires_at),
        )
        conn.commit()

 # Bucket operations
 def get_buckets(self, portfolio_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get buckets, optionally filtered by portfolio"""
    with self.get_connection() as conn:
        if portfolio_id:
            cursor = conn.execute(
                "SELECT * FROM buckets WHERE portfolio_id = ? ORDER BY created_at DESC",
                (portfolio_id,),
            )
        else:
            cursor = conn.execute("SELECT * FROM buckets ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

 def create_bucket(
    self,
    portfolio_id: int,
    name: str,
    start_value: float = 0,
    notes: Optional[str] = None,
 ) -> Dict[str, Any]:
    """Create new bucket"""
    with self.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO buckets (portfolio_id, name, start_value, notes) VALUES (?, ?, ?, ?)",
            (portfolio_id, name, start_value, notes),
        )
        bucket_id = cursor.lastrowid
        conn.commit()

        cursor = conn.execute("SELECT * FROM buckets WHERE id = ?", (bucket_id,))
        return dict(cursor.fetchone())

# Global database instance
db = DatabaseManager()
