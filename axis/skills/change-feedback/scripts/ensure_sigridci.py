import os
import shutil
import subprocess
import sys

SIGRIDCI_REPOSITORY = "https://github.com/Software-Improvement-Group/sigridci.git"


def user_cache_dir():
    if sys.platform == "win32":
        return os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches")
    return os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")


def agents_py_path(sigridci_dir):
    return os.path.join(sigridci_dir, "sigridci", "agents.py")


def pull_latest(sigridci_dir):
    result = subprocess.run(["git", "-C", sigridci_dir, "pull", "--ff-only", "--quiet"])
    return result.returncode == 0


def clone_shallow(sigridci_dir):
    os.makedirs(os.path.dirname(sigridci_dir), exist_ok=True)
    result = subprocess.run(["git", "clone", "--depth", "1", SIGRIDCI_REPOSITORY, sigridci_dir])
    return result.returncode == 0


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def ensure_sigridci(sigridci_dir):
    if os.path.isfile(agents_py_path(sigridci_dir)):
        if pull_latest(sigridci_dir):
            return
        print("WARNING: Failed to update cached sigridci clone; re-cloning.", file=sys.stderr)
        shutil.rmtree(sigridci_dir)

    if not clone_shallow(sigridci_dir):
        fail("Failed to clone sigridci repository.")
    if not os.path.isfile(agents_py_path(sigridci_dir)):
        fail("Clone succeeded but agents.py not found at expected path.")


def main():
    sigridci_dir = os.path.join(user_cache_dir(), "sigrid", "sigridci")
    ensure_sigridci(sigridci_dir)
    print(sigridci_dir)


if __name__ == "__main__":
    main()
