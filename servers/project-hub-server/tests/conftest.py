"""Test configuration — uses an in-memory SQLite database."""
import sys
from pathlib import Path

import pytest

# Add the server directory to the path so tools can be imported directly
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch, tmp_path):
    """Redirect all DB operations to a temporary file-based SQLite database.

    Uses tmp_path (unique per test) so each test starts with a clean slate.
    """
    db_file = tmp_path / "test.db"

    def _fake_get_db_path():
        return db_file

    import tools.db as db_module
    monkeypatch.setattr(db_module, "get_db_path", _fake_get_db_path)

    # Initialize the schema in the temp DB
    from tools.db import init_db
    init_db()

    yield db_file
