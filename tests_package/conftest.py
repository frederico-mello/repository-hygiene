import subprocess

import pytest


@pytest.fixture
def git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init"], cwd=repo, capture_output=True, timeout=10, shell=False
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=repo,
        capture_output=True,
        timeout=10,
        shell=False,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=repo,
        capture_output=True,
        timeout=10,
        shell=False,
    )
    return repo
