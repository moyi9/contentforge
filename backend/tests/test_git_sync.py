import subprocess
import pytest
from pathlib import Path
from app.services.git_sync import GitSyncService


@pytest.fixture
def git_repo(tmp_path):
    """Create a bare git repo to use as remote"""
    repo = tmp_path / "vault"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@test.com"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "test"], check=True
    )
    (repo / "test.md").write_text("# Test")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=True)
    return str(repo)


def test_git_clone_if_not_exists(git_repo, tmp_path):
    clone_path = tmp_path / "clone"
    svc = GitSyncService(repo_url=git_repo, local_path=str(clone_path))
    result = svc.sync()
    assert result["status"] == "ok"
    assert (clone_path / "test.md").exists()
    assert (clone_path / "test.md").read_text() == "# Test"


def test_git_pull_if_exists(git_repo, tmp_path):
    clone_path = tmp_path / "clone"
    svc = GitSyncService(repo_url=git_repo, local_path=str(clone_path))
    svc.sync()  # first sync: clone

    # Add new commit to remote
    (Path(git_repo) / "new.md").write_text("# New file")
    subprocess.run(["git", "-C", git_repo, "add", "."], check=True)
    subprocess.run(["git", "-C", git_repo, "commit", "-m", "update"], check=True)

    result = svc.sync()  # second sync: pull
    assert result["status"] == "ok"
    assert (clone_path / "new.md").read_text() == "# New file"


def test_get_changed_files_empty(git_repo, tmp_path):
    clone_path = tmp_path / "clone3"
    svc = GitSyncService(repo_url=git_repo, local_path=str(clone_path))
    svc.sync()
    changes = svc.get_changed_files()
    assert len(changes) == 0
