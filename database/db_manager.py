import sqlite3
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file location
DATABASE_PATH = BASE_DIR / "data" / "learnsphere.db"

def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the initial database tables if they do not exist.
    """
    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS learner_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                preferred_language TEXT DEFAULT 'English',
                learning_level TEXT DEFAULT 'Beginner',
                save_learning_history INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_title TEXT,
                subject TEXT,
                topic TEXT,
                conversation_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                topic TEXT,
                difficulty TEXT,
                total_questions INTEGER,
                correct_answers INTEGER,
                score_percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS topic_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                topic TEXT,
                status TEXT DEFAULT 'Not Started',
                progress_percentage REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, topic)
            )
        """)

        # Document Intelligence registry
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                total_chunks INTEGER NOT NULL DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Learning Goals
        connection.execute("""
            CREATE TABLE IF NOT EXISTS learning_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                title TEXT NOT NULL,
                subject TEXT,
                topic TEXT,
                target_value REAL NOT NULL,
                deadline DATE NOT NULL,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def migrate_topic_progress_table():
    """
    Add a unique constraint to subject and topic
    while preserving existing progress records.
    """

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS topic_progress_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                topic TEXT,
                status TEXT DEFAULT 'Not Started',
                progress_percentage REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, topic)
            )
        """)

        connection.execute("""
            INSERT OR IGNORE INTO topic_progress_new (
                id,
                subject,
                topic,
                status,
                progress_percentage,
                updated_at
            )
            SELECT
                id,
                subject,
                topic,
                status,
                progress_percentage,
                updated_at
            FROM topic_progress
        """)

        connection.execute("DROP TABLE topic_progress")

        connection.execute("""
            ALTER TABLE topic_progress_new
            RENAME TO topic_progress
        """)


if __name__ == "__main__":
    initialize_database()
    migrate_topic_progress_table()
    print("AI LearnSphere database initialized successfully!")
