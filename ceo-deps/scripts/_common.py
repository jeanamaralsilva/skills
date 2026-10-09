"""Helpers shared by the ceo-deps scripts."""
import fnmatch
import os


def git_ignored(repo: str, rel_path: str) -> bool:
    """True when a .gitignore at the repo root ignores rel_path (simple patterns: name, /name, globs)."""
    try:
        with open(os.path.join(repo, ".gitignore"), encoding="utf-8", errors="ignore") as handle:
            patterns = [line.strip() for line in handle if line.strip() and not line.startswith("#") and not line.startswith("!")]
    except OSError:
        return False
    name = os.path.basename(rel_path)
    for pattern in patterns:
        anchored = pattern.startswith("/")
        pattern = pattern.lstrip("/").rstrip("/")
        if anchored and fnmatch.fnmatch(rel_path, pattern):
            return True
        if not anchored and (fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern)):
            return True
    return False
