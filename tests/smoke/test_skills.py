"""Smoke: skill frontmatter has required fields, valid model IDs, no duplicates."""
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

REQUIRED_FIELDS = {"name", "description", "model", "user-invocable"}
VALID_MODELS = {
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "claude-haiku-4-5-20251001",
}


def _load_frontmatter(skill_md: Path) -> dict:
    """Parse YAML frontmatter from a SKILL.md file."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def _all_skills() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def test_skills_directory_exists():
    assert SKILLS_DIR.exists(), f"skills/ directory not found: {SKILLS_DIR}"


def test_at_least_one_skill():
    skills = _all_skills()
    assert skills, "No SKILL.md files found under skills/"


def test_all_skills_have_required_fields():
    failures = []
    for skill_md in _all_skills():
        fm = _load_frontmatter(skill_md)
        missing = REQUIRED_FIELDS - set(fm.keys())
        if missing:
            failures.append(f"{skill_md.parent.name}: missing {sorted(missing)}")
    assert not failures, "Skills with missing frontmatter fields:\n" + "\n".join(failures)


def test_all_skills_have_valid_model():
    failures = []
    for skill_md in _all_skills():
        fm = _load_frontmatter(skill_md)
        model = fm.get("model", "")
        if model not in VALID_MODELS:
            failures.append(f"{skill_md.parent.name}: invalid model '{model}'")
    assert not failures, "Skills with invalid model IDs:\n" + "\n".join(failures)


def test_no_duplicate_skill_names():
    names = [_load_frontmatter(s).get("name", "") for s in _all_skills()]
    names = [n for n in names if n]
    assert len(names) == len(set(names)), (
        f"Duplicate skill names: {[n for n in names if names.count(n) > 1]}"
    )


def test_user_invocable_is_boolean():
    failures = []
    for skill_md in _all_skills():
        fm = _load_frontmatter(skill_md)
        value = fm.get("user-invocable")
        if not isinstance(value, bool):
            failures.append(f"{skill_md.parent.name}: user-invocable={value!r} (must be bool)")
    assert not failures, "Skills with non-boolean user-invocable:\n" + "\n".join(failures)


def test_add_contact_checks_for_duplicates_before_creating():
    """Regression test for #56: add-contact must search for existing contacts before
    saving a new one, unconditionally — not just on explicit request. Must use
    tool_search_contacts (unpaginated, cross-project) rather than the paginated
    tool_list_contacts/tool_list_shared_contacts, which can silently miss a match once a
    project or the shared directory grows past the default page size. Skipping the search
    entirely is exactly how duplicate contacts get created.
    """
    body = (SKILLS_DIR / "add-contact" / "SKILL.md").read_text(encoding="utf-8")

    search_pos = body.find("tool_search_contacts")
    save_pos = body.rfind("tool_add_contact(project_id")
    assert search_pos != -1, "add-contact must call tool_search_contacts()"
    assert save_pos != -1, "add-contact must document the tool_add_contact(project_id, ...) save call"
    assert search_pos < save_pos, (
        "tool_search_contacts() must be documented as happening before the tool_add_contact() "
        "save call, so existing contacts are checked before a new one is created"
    )

    # The check must be unconditional, not gated behind an explicit user request — verify
    # the "unconditional" language sits near the search call, not just anywhere in the file.
    window = body[max(0, search_pos - 200):search_pos + 400].lower()
    assert "unconditionally" in window or "immer" in window, (
        "add-contact must state near the tool_search_contacts() call that the duplicate "
        "check happens unconditionally, not only when the user explicitly asks to see "
        "existing contacts first"
    )


def test_edit_note_guards_against_missing_note_and_cross_project_note():
    """Regression test: edit-note's Step 2 not-found guard must stop before Step 3, and
    tool_get_note is not project-scoped server-side (SELECT * FROM notes WHERE id = ?,
    no project_id filter — servers/project-hub-server/tools/notes.py), so the skill itself
    must reject a note that doesn't belong to the active project rather than silently
    editing it.
    """
    body = (SKILLS_DIR / "edit-note" / "SKILL.md").read_text(encoding="utf-8")

    not_found_pos = body.find("nicht gefunden")
    get_note_pos = body.find("tool_get_note(note_id)")
    project_scope_pos = body.find("project_id")
    step3_pos = body.find("### 3. Show Current Content")

    assert get_note_pos != -1, "edit-note must call tool_get_note(note_id)"
    assert not_found_pos != -1, "edit-note must document a 'nicht gefunden' guard"
    assert project_scope_pos != -1, (
        "edit-note must check the loaded note's project_id against the active project"
    )
    assert get_note_pos < not_found_pos < step3_pos, (
        "the not-found guard must be documented between the tool_get_note call and Step 3"
    )
    assert get_note_pos < project_scope_pos < step3_pos, (
        "the cross-project scoping check must be documented between the tool_get_note call "
        "and Step 3, so a note from another project is rejected before it is ever displayed"
    )


def test_edit_note_type_whitelist_matches_server_subfolders():
    """Regression test: the server never validates note_type (no CHECK constraint on
    notes.type — servers/project-hub-server/tools/db.py), so the skill's whitelist in Step 4
    is the only thing preventing garbage types from being written. It must keep listing
    exactly the five types docs_writer.py knows how to file (_TYPE_TO_SUBFOLDER).
    """
    body = (SKILLS_DIR / "edit-note" / "SKILL.md").read_text(encoding="utf-8")
    expected_types = {"note", "meeting-notes", "email", "decision", "action-item"}

    whitelist_pos = body.find("exact match to one of the five documented types")
    assert whitelist_pos != -1, (
        "edit-note must document that type changes are restricted to an exact match "
        "against the supported types"
    )
    window = body[whitelist_pos:whitelist_pos + 200]
    for note_type in expected_types:
        assert note_type in window, f"edit-note type whitelist is missing '{note_type}'"


def test_delete_testdata_prefix_gate_precedes_any_tool_call():
    """Regression guard (project-hub#82): delete-testdata's zz-sandbox- prefix refusal
    must be documented as step 1, before any MCP tool call — this is the exact ordering
    skill-rollout's onboarding live-verifies (it calls this skill with a synthetic,
    non-prefixed slug and expects refusal before any lookup happens). A future edit that
    silently reorders the safety check after a tool call would defeat the whole guard.
    """
    body = (SKILLS_DIR / "delete-testdata" / "SKILL.md").read_text(encoding="utf-8")

    gate_pos = body.find("Prefix gate")
    get_project_pos = body.find("tool_get_project")
    delete_project_pos = body.find("tool_delete_project")

    assert gate_pos != -1, "delete-testdata must document a 'Prefix gate' step"
    assert get_project_pos != -1, "delete-testdata must call tool_get_project"
    assert delete_project_pos != -1, "delete-testdata must call tool_delete_project"
    assert gate_pos < get_project_pos < delete_project_pos, (
        "delete-testdata's prefix gate must be documented before tool_get_project, "
        "which must in turn happen before tool_delete_project — refusing after a lookup "
        "has already run defeats the safety property"
    )
