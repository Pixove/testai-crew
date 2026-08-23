"""Pytest fixtures for the automated orders test suite."""

import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pytest

SAMPLE_DB = Path(__file__).resolve().parents[1] / "sample.db"


@pytest.fixture()
def db_conn():
    """Return a connection to a temporary copy of the sample database."""
    source_path = SAMPLE_DB
    fd, tmp_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    shutil.copy2(source_path, tmp_path)
    conn = sqlite3.connect(tmp_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
    finally:
        conn.close()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
