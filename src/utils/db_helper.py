"""
Database Helper Utility for E-Commerce Sales & Customer Analytics.
Provides connection handling, schema deployment, query execution, and DataFrame conversion.
"""

import sqlite3
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "ecommerce_analytics.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(db_path=None):
    """Establishes and returns a sqlite3 connection with foreign keys enabled."""
    target_path = Path(db_path) if db_path else DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path=None, schema_path=None):
    """Executes the schema DDL to create/reset tables and indexes."""
    s_path = Path(schema_path) if schema_path else SCHEMA_PATH
    if not s_path.exists():
        raise FileNotFoundError(f"Schema file not found at {s_path}")

    with open(s_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(schema_sql)
        print(f"[DB] Initialized database schema successfully at: {db_path or DB_PATH}")
    finally:
        conn.close()


def run_query(query, params=None, db_path=None):
    """Executes a SQL query and returns rows as list of dicts."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def run_sql_file(file_path, db_path=None):
    """Reads a SQL query from file and returns the result as list of dicts."""
    fpath = Path(file_path)
    if not fpath.exists():
        raise FileNotFoundError(f"SQL file not found at: {fpath}")

    with open(fpath, "r", encoding="utf-8") as f:
        sql = f.read()

    # If there are multiple statements, split and execute
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        results = []
        for stmt in statements:
            cursor.execute(stmt)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                results.append([dict(zip(columns, row)) for row in rows])
        return results[-1] if results else []
    finally:
        conn.close()
