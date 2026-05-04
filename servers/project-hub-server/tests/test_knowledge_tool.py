"""Tests for the knowledge tool functions (save/get/list/delete)."""
import pytest
from tools.knowledge import delete_knowledge, get_all_knowledge, get_knowledge, list_knowledge, save_knowledge


@pytest.fixture
def knowledge_root(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.knowledge.get_knowledge_root", lambda: tmp_path)
    return tmp_path


def test_save_and_get_roundtrip(knowledge_root):
    saved = save_knowledge("generic", "governance", "# Governance\n\nContent here.")
    assert saved["topic"] == "governance"
    assert saved["title"] == "Governance"
    assert "Content here." in saved["content"]

    fetched = get_knowledge("generic", "governance")
    assert fetched is not None
    assert fetched["content"] == saved["content"]


def test_get_knowledge_not_found(knowledge_root):
    assert get_knowledge("generic", "nonexistent") is None


def test_save_overwrites_existing(knowledge_root):
    save_knowledge("generic", "process", "# Process\n\nVersion 1.")
    updated = save_knowledge("generic", "process", "# Process\n\nVersion 2.")
    assert "Version 2." in updated["content"]


def test_list_knowledge_returns_topics(knowledge_root):
    save_knowledge("it-project", "architecture", "# Architecture\n\nDiagram.")
    save_knowledge("it-project", "charter", "# Charter\n\nGoals.")

    items = list_knowledge("it-project")
    topics = {i["topic"] for i in items}
    assert topics == {"architecture", "charter"}


def test_list_knowledge_extracts_h1_title(knowledge_root):
    save_knowledge("generic", "roles", "# Role Matrix\n\nContent.")

    items = list_knowledge("generic")
    assert items[0]["title"] == "Role Matrix"


def test_list_knowledge_falls_back_to_stem_when_no_h1(knowledge_root):
    save_knowledge("generic", "notes", "No heading here.")

    items = list_knowledge("generic")
    assert items[0]["title"] == "notes"


def test_list_knowledge_empty_returns_empty(knowledge_root):
    assert list_knowledge("generic") == []


def test_get_all_knowledge_loads_full_content(knowledge_root):
    save_knowledge("consulting", "engagement", "# Engagement\n\nFull content.")
    save_knowledge("consulting", "process", "# Process\n\nSteps.")

    all_items = get_all_knowledge("consulting")
    assert len(all_items) == 2
    assert all("content" in item for item in all_items)


def test_delete_knowledge_removes_file(knowledge_root):
    save_knowledge("generic", "to-delete", "# Delete Me")

    result = delete_knowledge("generic", "to-delete")

    assert result is True
    assert get_knowledge("generic", "to-delete") is None


def test_delete_knowledge_not_found_returns_false(knowledge_root):
    assert delete_knowledge("generic", "does-not-exist") is False


def test_save_knowledge_path_traversal_rejected(knowledge_root):
    with pytest.raises(ValueError, match="Invalid topic"):
        save_knowledge("generic", "../../etc/passwd", "malicious")


def test_get_knowledge_path_traversal_rejected(knowledge_root):
    with pytest.raises(ValueError, match="Invalid topic"):
        get_knowledge("generic", "../escape")


def test_delete_knowledge_path_traversal_rejected(knowledge_root):
    with pytest.raises(ValueError, match="Invalid topic"):
        delete_knowledge("generic", "../../sensitive")
