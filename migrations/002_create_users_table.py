"""
Migration: Create users table
Version: 002
Description: Creates the users table for authentication
"""

import sqlite3
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_PATH


def upgrade():
    """Apply the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create migrations tracking table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if this migration has already been applied
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("002_create_users_table",))
    if cursor.fetchone():
        print("Migration 002_create_users_table already applied. Skipping.")
        conn.close()
        return
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Record this migration as applied
    cursor.execute("INSERT INTO _migrations (name) VALUES (?)", ("002_create_users_table",))
    
    conn.commit()
    conn.close()
    print("Migration 002_create_users_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Drop users table
    cursor.execute("DROP TABLE IF EXISTS users")
    
    # Remove from migrations table
    cursor.execute("DELETE FROM _migrations WHERE name = ?", ("002_create_users_table",))
    
    conn.commit()
    conn.close()
    print("Migration 002_create_users_table reverted successfully.")
