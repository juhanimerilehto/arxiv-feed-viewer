#!/usr/bin/env python3
"""
Initialize the database with tables and FTS5 virtual table.
Run this script once before first use.
"""
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_db
from backend.config import settings

def main():
    print("Initializing database...")
    print(f"Database path: {settings.DATABASE_PATH}")

    # Ensure data directory exists
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_db()

    print("Database initialized successfully!")
    print(f"Database created at: {db_path.absolute()}")

if __name__ == "__main__":
    main()
