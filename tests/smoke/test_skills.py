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


def test_status_update_identifier_must_be_slug_not_project_id():
    """Regression guard: status's update step must document that
    tool_update_project(identifier, ...) needs the project's slug/name — never the numeric
    project_id from tool_get_session()/tool_get_project_by_id(). update_project() matches
    via `WHERE slug = ? OR LOWER(name) = LOWER(?)` (servers/project-hub-server/tools/
    projects.py), so a numeric identifier silently matches nothing.
    """
    body = (SKILLS_DIR / "status" / "SKILL.md").read_text(encoding="utf-8")

    assert "never the numeric `project_id`" in body or "never the numeric project_id" in body, (
        "status must explicitly warn that tool_update_project's identifier is the slug/name, "
        "never the numeric project_id"
    )
    assert "None" in body and "gefunden" in body, (
        "status must document what happens when tool_update_project returns None/empty "
        "(wrong identifier) instead of unconditionally printing the success confirmation"
    )


def test_status_contact_bucketing_uses_type_field():
    """Regression guard: status's contact table bucketing must key off the `type` field on
    each contact row, not `contact_type` (which is only a tool parameter name on add/update/
    list, never a field on the row itself). Mixing the two up would make every contact fail
    the `type == "external"` check and pile into "Interne Kontakte" instead.
    """
    body = (SKILLS_DIR / "status" / "SKILL.md").read_text(encoding="utf-8")

    assert 'type == "external"' in body, (
        'status must document the contact bucketing rule as `type == "external"`'
    )
    assert "`contact_type` is" in body or "contact_type` is only" in body, (
        "status must clarify that `contact_type` is a tool parameter name, distinct from "
        "the `type` field on the returned contact row"
    )
