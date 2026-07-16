"""Smoke: Windows/POSIX MCP server launch — regression guard for #61."""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
MCP_JSON = ROOT / ".mcp.json"
RUN_SERVER = ROOT / "bin" / "run-server"
RUN_SERVER_CMD = ROOT / "bin" / "run-server.cmd"

SKILLS_REQUIRING_OS_BRANCH = [
    ROOT / "skills" / "setup" / "SKILL.md",
    ROOT / "skills" / "session-start" / "SKILL.md",
    ROOT / "skills" / "configure" / "SKILL.md",
]

SKILLS_REQUIRING_PY_LAUNCHER_FALLBACK = [
    ROOT / "skills" / "setup" / "SKILL.md",
    ROOT / "skills" / "session-start" / "SKILL.md",
]


def test_mcp_json_is_valid_json():
    json.loads(MCP_JSON.read_text(encoding="utf-8"))


def test_mcp_json_command_has_no_hardcoded_venv_subpath():
    """command must go through the OS-agnostic bin/run-server wrapper, not hardcode
    venv/bin (POSIX) or venv\\Scripts (Windows) directly — that's exactly bug #61."""
    config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    command = config["mcpServers"]["project-hub-mcp"]["command"]
    assert "venv/bin" not in command
    assert "venv\\Scripts" not in command and "venv/Scripts" not in command
    assert command.endswith("bin/run-server")


def test_mcp_json_schema():
    """A dropped/typo'd field here silently breaks the MCP server for every user."""
    config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    server = config["mcpServers"]["project-hub-mcp"]
    assert server["type"] == "stdio"
    assert isinstance(server["args"], list) and len(server["args"]) == 1
    assert "CLAUDE_PLUGIN_ROOT" in server["env"]


def test_run_server_wrapper_exists_and_is_executable():
    assert RUN_SERVER.exists(), "bin/run-server not found"
    assert os.access(RUN_SERVER, os.X_OK), "bin/run-server must have the executable bit set"
    first_line = RUN_SERVER.read_text(encoding="utf-8").splitlines()[0]
    assert first_line in ("#!/bin/sh", "#!/bin/bash"), f"unexpected shebang: {first_line}"


def test_run_server_cmd_wrapper_targets_windows_venv():
    assert RUN_SERVER_CMD.exists(), "bin/run-server.cmd not found"
    content = RUN_SERVER_CMD.read_text(encoding="utf-8")
    assert "%USERPROFILE%" in content
    assert "Scripts\\python.exe" in content


def test_setup_session_configure_skills_document_both_platforms():
    """Regression guard: a file that documents only the POSIX venv path (venv/bin/python3)
    without a Windows equivalent (venv\\Scripts\\python.exe) is exactly the #61 bug —
    check both markers are present together, not that the POSIX one is absent (it must
    legitimately remain, for the POSIX branch)."""
    for skill_md in SKILLS_REQUIRING_OS_BRANCH:
        body = skill_md.read_text(encoding="utf-8")
        assert "venv/bin/python3" in body or "venv/bin/pip" in body, (
            f"{skill_md}: missing POSIX venv interpreter path"
        )
        assert "Scripts\\python.exe" in body or "Scripts\\pip.exe" in body, (
            f"{skill_md}: missing Windows venv interpreter path — likely not yet "
            f"OS-branched (regression for #61)"
        )


def test_setup_session_configure_skills_have_matching_path_counts():
    """Catches a copy-paste swap (e.g. a Windows bullet showing the POSIX path) that
    the plain presence check above wouldn't — POSIX and Windows mentions should pair up."""
    for skill_md in SKILLS_REQUIRING_OS_BRANCH:
        body = skill_md.read_text(encoding="utf-8")
        posix = len(re.findall(r"venv/bin/(?:python3|pip)", body))
        windows = len(re.findall(r"Scripts\\(?:python\.exe|pip\.exe)", body))
        assert posix == windows, (
            f"{skill_md}: POSIX/Windows path mention count mismatch ({posix} vs {windows})"
        )


def test_setup_and_session_start_document_py_launcher_fallback():
    """Regression guard for #69: on managed Windows devices, bare `python`/`python3`
    can resolve to the Microsoft Store app-execution-alias stub (exit code 49) even
    when Python is genuinely installed. `py -3` (the Python Launcher, always on PATH)
    must be documented as a fallback, or setup/session-start silently tell a managed
    device user to install Python they already have."""
    for skill_md in SKILLS_REQUIRING_PY_LAUNCHER_FALLBACK:
        body = skill_md.read_text(encoding="utf-8")
        assert "py -3" in body, (
            f"{skill_md}: missing `py -3` fallback for Windows Store-alias detection failures"
        )


def test_setup_step3_venv_creation_uses_resolved_interpreter_not_hardcoded():
    """Regression guard for #69: venv creation must reuse whichever interpreter Step 0
    resolved (<PY>), not hardcode `python`/`python3` — hardcoding breaks again exactly
    where Step 0 just worked around a Store-alias failure."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    step3 = body.split("### Step 3:", 1)[1].split("### Step 4:", 1)[0]
    assert "<PY> -m venv" in step3, "Step 3 must invoke <PY>, not a hardcoded python/python3"
    assert not re.search(r"^- (?:POSIX|Windows): `python3? -m venv", step3, re.MULTILINE), (
        "Step 3 still hardcodes python/python3 for venv creation"
    )


def test_setup_steps_1_2_5_use_resolved_interpreter_not_hardcoded():
    """Regression guard for #69: Steps 1, 2, and 5 (system-level Python invocations
    before the venv exists) must all reuse <PY> from Step 0, not hardcode python3 —
    the same bug Step 3 already guards against, just for the other three call sites."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    for start, end, label in [
        ("### Step 1:", "### Step 2:", "Step 1"),
        ("### Step 2:", "### Step 3:", "Step 2"),
        ("### Step 5:", "### Step 5b:", "Step 5"),
    ]:
        section = body.split(start, 1)[1].split(end, 1)[0]
        assert "<PY> -c" in section, f"{label} must invoke <PY>, not a hardcoded python3"
        assert not re.search(r"^python3? -c", section, re.MULTILINE), (
            f"{label} still hardcodes python3/python"
        )


def test_setup_documents_windows_quoting_note_for_py_fallback():
    """Regression guard: PowerShell call-operator quoting note for space-containing
    full paths from the known-install fallback must stay present — without it, an
    Intune-managed device whose Python only resolves via C:\\Program Files\\... fails
    on the exact scenario #69 was filed for."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    assert "Windows quoting note" in body
    assert '& "<PY>"' in body


def test_setup_known_install_fallback_uses_powershell_env_syntax():
    """Regression guard: known-install-path hints must use PowerShell $env: syntax,
    not cmd %VAR% syntax — they sit inside PowerShell call-operator commands, %VAR%
    would silently fail to expand there."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    assert "$env:ProgramFiles" in body
    assert "%ProgramFiles%" not in body
    assert "%LocalAppData%" not in body


def test_setup_step5b_uses_claude_plugin_root_not_candidate_guessing():
    """Regression guard for #70: Step 5b must use the interpolated ${CLAUDE_PLUGIN_ROOT}
    (already proven to work in Steps 4/5/6) instead of guessing the plugin root via a
    hardcoded candidate-path search — the candidate list didn't include the actual cache
    path and could silently install knowledge templates from the wrong version, or skip
    them entirely, once cache and checkout diverge."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    step5b = body.split("### Step 5b:", 1)[1].split("### Step 6:", 1)[0]
    assert "${CLAUDE_PLUGIN_ROOT}/knowledge" in step5b, (
        "Step 5b must interpolate ${CLAUDE_PLUGIN_ROOT} like Steps 4/5/6 do"
    )
    assert "candidates" not in step5b, (
        "Step 5b still guesses the plugin root via a candidate-path search (regression for #70)"
    )
    assert "PLUGIN_ROOT_NOT_FOUND" not in step5b, (
        "Step 5b still has the silent-skip fallback from the candidate-guessing heuristic"
    )


def _extract_python_block(section_text):
    """Pull the content of the first ```python fenced block out of a SKILL.md section."""
    match = re.search(r"```python\n(.*?)```", section_text, re.DOTALL)
    assert match, "no ```python fenced block found in section"
    return match.group(1)


def test_setup_step5b_script_copies_new_but_never_overwrites_existing():
    """Real execution of Step 5b's embedded script, not just a text check. This is the
    exact mechanism the #70 breaking-change analysis relies on to argue re-running setup
    is safe: templates are copied once but never overwritten on a later run, so a user's
    own edits to a placeholder file survive. That guarantee had zero executable coverage —
    close it by running the actual script against a real directory tree, twice."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    step5b = body.split("### Step 5b:", 1)[1].split("### Step 6:", 1)[0]
    script = _extract_python_block(step5b)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_root = tmp_path / "plugin_root"
        (plugin_root / "knowledge" / "generic").mkdir(parents=True)
        (plugin_root / "knowledge" / "generic" / "charter.md").write_text("ORIGINAL TEMPLATE")

        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()
        env = {**os.environ, "HOME": str(fake_home), "USERPROFILE": str(fake_home)}

        resolved_script = script.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root))
        dest_file = fake_home / ".project-hub" / "knowledge" / "generic" / "charter.md"

        # First run: nothing installed yet -> must copy.
        result = subprocess.run(
            [sys.executable, "-c", resolved_script], env=env, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"first run failed: {result.stderr}"
        assert dest_file.exists(), "first run must install the template"
        assert dest_file.read_text() == "ORIGINAL TEMPLATE"

        # Simulate the user editing their placeholder.
        dest_file.write_text("USER EDITED CONTENT")

        # Second run: file already exists -> must NOT overwrite the user's edit.
        result = subprocess.run(
            [sys.executable, "-c", resolved_script], env=env, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"second run failed: {result.stderr}"
        assert dest_file.read_text() == "USER EDITED CONTENT", (
            "Step 5b overwrote an already-installed template — this would silently destroy "
            "user-authored content on every /project-hub:setup re-run"
        )


def test_claude_plugin_root_interpolation_survives_windows_backslash_paths():
    """Regression guard: ${CLAUDE_PLUGIN_ROOT} can be interpolated as a Windows path
    containing backslashes (e.g. C:\\Users\\...\\project-hub). Embedded in a plain
    (non-raw) Python string literal, a stray \\U/\\u/\\N sequence becomes an invalid
    Unicode escape and the script fails with a SyntaxError before it even runs — this
    broke test_setup_step5b_script_copies_new_but_never_overwrites_existing for real on
    Windows CI. Verify Steps 5, 5b, and 6 all use a raw string, so this can't recur
    regardless of which OS actually generates the substituted path (checked here via
    compile(), not subprocess, so it runs identically on every CI platform)."""
    body = (ROOT / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
    fake_windows_root = r"C:\Users\RUNNER~1\AppData\Local\Temp\plugin_root"
    for start, end, label in [
        ("### Step 5:", "### Step 5b:", "Step 5"),
        ("### Step 5b:", "### Step 6:", "Step 5b"),
        ("### Step 6:", "### Step 7:", "Step 6"),
    ]:
        section = body.split(start, 1)[1].split(end, 1)[0]
        script = _extract_python_block(section)
        resolved = script.replace("${CLAUDE_PLUGIN_ROOT}", fake_windows_root)
        try:
            compile(resolved, f"<{label}>", "exec")
        except SyntaxError as e:
            raise AssertionError(
                f"{label}: script is not valid Python once ${{CLAUDE_PLUGIN_ROOT}} is "
                f"substituted with a Windows backslash path — missing raw string (r'...')"
                f" around the placeholder: {e}"
            ) from e


def test_run_server_wrapper_actually_launches_python():
    """Real subprocess spawn through the OS-appropriate wrapper — proves shebang
    execution / %USERPROFILE%-%*-quoting actually work, not just that the files exist."""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        if sys.platform == "win32":
            venv_scripts = home / ".project-hub" / "venv" / "Scripts"
            venv_scripts.mkdir(parents=True)
            (venv_scripts / "python.exe").write_bytes(Path(sys.executable).read_bytes())
            env = {**os.environ, "USERPROFILE": str(home)}
            cmd = [str(RUN_SERVER_CMD), "-c", "print('OK')"]
        else:
            venv_bin = home / ".project-hub" / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            (venv_bin / "python3").symlink_to(sys.executable)
            env = {**os.environ, "HOME": str(home)}
            cmd = [str(RUN_SERVER), "-c", "print('OK')"]

        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, f"wrapper failed: {result.stderr}"
        assert "OK" in result.stdout
