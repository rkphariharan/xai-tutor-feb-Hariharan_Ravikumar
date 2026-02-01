"""
Migration: Create folders table
Version: 003
Description: Creates the folders table for hierarchical folder structure
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
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("003_create_folders_table",))
    if cursor.fetchone():
        print("Migration 003_create_folders_table already applied. Skipping.")
        conn.close()
        return
    
    # Create folders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            parent_folder_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_folder_id) REFERENCES folders(id) ON DELETE CASCADE
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_folders_user_id 
        ON folders(user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_folders_parent_id 
        ON folders(parent_folder_id)
    """)
    
    # Record this migration as applied
    cursor.execute("INSERT INTO _migrations (name) VALUES (?)", ("003_create_folders_table",))
    
    conn.commit()
    conn.close()
    print("Migration 003_create_folders_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Drop indexes
    cursor.execute("DROP INDEX IF EXISTS idx_folders_parent_id")
    cursor.execute("DROP INDEX IF EXISTS idx_folders_user_id")
    
    # Drop folders table
    cursor.execute("DROP TABLE IF EXISTS folders")
    
    # Remove from migrations table
    cursor.execute("DELETE FROM _migrations WHERE name = ?", ("003_create_folders_table",))
    
    conn.commit()
    conn.close()
    print("Migration 003_create_folders_table reverted successfully.")
