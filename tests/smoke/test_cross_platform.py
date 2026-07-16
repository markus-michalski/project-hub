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
