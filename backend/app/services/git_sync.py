import subprocess
from pathlib import Path


class GitSyncService:
    def __init__(self, repo_url: str, local_path: str):
        self.repo_url = repo_url
        self.local_path = Path(local_path)
        self._last_commit = None

    def sync(self) -> dict:
        if self.local_path.exists():
            return self._pull()
        else:
            return self._clone()

    def _clone(self) -> dict:
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", self.repo_url, str(self.local_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr.strip()}
        self._last_commit = self._get_head_commit()
        return {"status": "ok"}

    def _pull(self) -> dict:
        result = subprocess.run(
            ["git", "-C", str(self.local_path), "pull", "origin", "main"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            # Try 'master' if 'main' failed
            result = subprocess.run(
                ["git", "-C", str(self.local_path), "pull", "origin", "master"],
                capture_output=True, text=True,
            )
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr.strip()}
        self._last_commit = self._get_head_commit()
        return {"status": "ok"}

    def get_changed_files(self) -> list[str]:
        current = self._get_head_commit()
        if self._last_commit and current != self._last_commit:
            result = subprocess.run(
                [
                    "git", "-C", str(self.local_path), "diff", "--name-only",
                    self._last_commit, current,
                ],
                capture_output=True, text=True,
            )
            return [f for f in result.stdout.strip().split("\n") if f]
        return []

    def _get_head_commit(self) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.local_path), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        return result.stdout.strip()
