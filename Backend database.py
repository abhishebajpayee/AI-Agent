import sqlite3
from datetime import datetime
from typing import Dict, List, Any

DB_NAME = "agent_data.db"

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            upload_timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_metadata (
            metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            sheet_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            semantic_description TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files (file_id)
        )
    """)
    conn.commit()
    conn.close()

def store_file_metadata(file_id: str, file_name: str, column_metadata: Dict[str, Dict[str, str]]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Use a dummy user_id for this assignment
    cursor.execute(
        "INSERT INTO files (file_id, user_id, file_name, upload_timestamp) VALUES (?, ?, ?, ?)",
        (file_id, 1, file_name, datetime.now().isoformat())
    )
    
    metadata_records = []
    for sheet_name, cols in column_metadata.items():
        for column_name, description in cols.items():
            metadata_records.append((file_id, sheet_name, column_name, description))

    cursor.executemany(
        """INSERT INTO file_metadata (file_id, sheet_name, column_name, semantic_description) 
           VALUES (?, ?, ?, ?)""",
        metadata_records
    )

    conn.commit()
    conn.close()

def retrieve_metadata_for_file(file_id: str) -> List[Dict[str, str]]:
    """Retrieves all metadata for a given file_id, used to prime the AI Agent."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT sheet_name, column_name, semantic_description FROM file_metadata WHERE file_id = ?", 
        (file_id,)
    )
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results
