"""
cricketzone/database.py — SQLite Connection & Schema
"""

import sqlite3
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv  = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def execute_db(sql, args=()):
    db  = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


def init_db():
    from cricketzone.models import seed_products

    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL CHECK(category IN ('bat','ball','kit')),
            description TEXT    NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            image       TEXT    NOT NULL DEFAULT 'placeholder.jpg',
            brand       TEXT,
            weight      TEXT,
            material    TEXT,
            size        TEXT,
            grade       TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS orders (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id       TEXT    NOT NULL UNIQUE,
            customer_name  TEXT    NOT NULL,
            customer_email TEXT    NOT NULL,
            customer_phone TEXT,
            product_id     INTEGER NOT NULL REFERENCES products(id),
            quantity       INTEGER NOT NULL DEFAULT 1,
            total_price    REAL    NOT NULL,
            address        TEXT    NOT NULL,
            status         TEXT    NOT NULL DEFAULT 'Confirmed',
            created_at     TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT NOT NULL,
            subject    TEXT,
            message    TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS admin_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            action     TEXT NOT NULL,
            detail     TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    db.commit()

    count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        seed_products(db)
        print("[CricketZone] Database seeded with 20 products.")
    else:
        print("[CricketZone] Database ready.")