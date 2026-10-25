"""Khởi tạo database SQLite và dữ liệu demo cho Iron Việt Fitness.

Chạy từ thư mục gym_center/api:
    python scripts/init_db.py
    python scripts/init_db.py --db data/gym_center.db
    python scripts/init_db.py --reset  # xoá DB đích cũ rồi tạo lại từ đầu

Dữ liệu demo được tạo bởi app.core.init_db() từ knowledge base của gym.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parent.parent
GYM_DIR = API_DIR.parent
sys.path.insert(0, str(API_DIR))

from app.core import DB_PATH as DEFAULT_DB_PATH, init_db  # noqa: E402


def initialize_database(db_path: Path, reset: bool = False) -> dict[str, int]:
    """Initialize the gym database and return row counts for its main tables."""
    db_path = db_path.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # app.core reads GYM_DB_PATH at import time. The CLI's --db option is
    # therefore passed through the environment before importing in normal use;
    # for this already-imported module, temporarily update its DB_PATH directly.
    import app.core as core
    original_path = core.DB_PATH
    core.DB_PATH = db_path
    try:
        if reset and db_path.exists():
            db_path.unlink()
        init_db()
        with sqlite3.connect(db_path) as conn:
            table_names = ("members", "memberships", "bookings", "requests", "payments")
            counts = {
                table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in table_names
            }
        return counts
    finally:
        core.DB_PATH = original_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Khởi tạo database demo Iron Việt Fitness")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Đường dẫn SQLite database")
    parser.add_argument("--reset", action="store_true", help="Xoá database đích trước khi tạo lại")
    args = parser.parse_args()

    counts = initialize_database(args.db, reset=args.reset)
    print(f"Đã khởi tạo database: {args.db.resolve()}")
    for table, count in counts.items():
        print(f"  {table:<14} {count:>5}")
