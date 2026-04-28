import os
from pathlib import Path

def get_project_root():
    """Returns absolute path to project root."""
    return Path(__file__).resolve().parent.parent.parent

def get_db_path(relative_path="backend/storage/sqlite_db/memory.db"):
    """Returns absolute path to a database file."""
    return str(get_project_root() / relative_path)

def ensure_dir(path):
    """Ensures directory exists for a given file path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
