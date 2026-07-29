import subprocess
from pathlib import Path

import pytest

from auditoria_higiene.commit_check import validar_commits


@pytest.fixture
def git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"], cwd=repo, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    return repo


def _commit(repo, message, filename):
    path = repo / filename
    path.write_text(message, encoding="utf-8")
    subprocess.run(["git", "add", filename], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True)


def test_valid_conventional_commit_has_no_finding(git_repo):
    _commit(git_repo, "feat(auth): add OAuth2 support", "auth.txt")

    assert validar_commits(str(git_repo)) == []


def test_invalid_commit_reports_hash_and_message(git_repo):
    _commit(git_repo, "added OAuth2 support", "auth.txt")

    findings = validar_commits(str(git_repo))

    assert len(findings) == 1
    assert findings[0]["regra"] == "commits_convencionais"
    assert findings[0]["severidade"] == "warning"
    assert len(findings[0]["caminho"]) == 40
    assert "Conventional Commits" in findings[0]["mensagem"]


def test_empty_repository_returns_no_findings(git_repo):
    assert validar_commits(str(git_repo)) == []


def test_missing_git_reports_system_error(tmp_path, monkeypatch):
    def missing_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", missing_git)

    findings = validar_commits(str(tmp_path))

    assert findings[0]["severidade"] == "error"
    assert "git" in findings[0]["mensagem"]
