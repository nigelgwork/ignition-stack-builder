#!/usr/bin/env python3
"""
Database migration script - Creates initial schema
This script applies the init.sql migration to the database
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def run_migration():
    """Apply the init.sql migration to the database"""
    # Get database connection parameters
    db_host = os.getenv("AUTH_DB_HOST", "localhost")
    db_port = os.getenv("AUTH_DB_PORT", "5432")
    db_name = os.getenv("AUTH_DB_NAME", "stack_builder_auth")
    db_user = os.getenv("AUTH_DB_USER", "stack_builder")
    db_password = os.getenv("AUTH_DB_PASSWORD", "changeme")

    print(f"Connecting to database at {db_host}:{db_port}/{db_name}...")

    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Read SQL migration file
        sql_file = Path(__file__).parent / "init.sql"
        print(f"Reading SQL migration from {sql_file}...")

        with open(sql_file, "r") as f:
            sql_content = f.read()

        # Execute SQL migration
        print("Applying migration...")
        cursor.execute(sql_content)

        print("✓ Migration completed successfully!")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"✗ SQL file not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
