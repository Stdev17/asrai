"""Exercise commit policy with real histories, never another project's commit ids."""

import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(repo, *args, input_text=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(args, cwd=repo, env=env, capture_output=True, text=True, input=input_text)


def git(repo, *args):
    result = run(repo, "git", *args)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def setup(repo):
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test Author")
    git(repo, "config", "user.email", "author@example.com")
    git(repo, "config", "core.hooksPath", "tools/hooks")
    shutil.copytree(ROOT / "tools", repo / "tools", ignore=shutil.ignore_patterns("__pycache__"))


def message(owners, trailers="", subject="chore(process): keep checks reproducible"):
    return (f"{subject}\n\nContributors need evidence from this repository.\n\n"
            f"Owners: {owners}\n{trailers}"
            "Signed-off-by: Test Author <author@example.com>\n")


def stage(repo, path, text):
    file = repo / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")
    git(repo, "add", path)


def rejected(repo, msg, fragment, *args):
    before = git(repo, "rev-parse", "HEAD")
    result = run(repo, "git", "commit", *args, "-m", msg)
    assert result.returncode != 0, result.stdout + result.stderr
    assert fragment in result.stdout + result.stderr, result.stdout + result.stderr
    assert git(repo, "rev-parse", "HEAD") == before, "rejected commit moved HEAD"


def test_commit_hooks_check_actual_trees_including_amend_and_worktrees(tmp_path):
    repo = tmp_path / "repo"
    setup(repo)
    git(repo, "add", "tools")
    git(repo, "commit", "-m", message("process"))
    root = git(repo, "rev-parse", "HEAD")

    stage(repo, "src/asrai/limit.py", "LIMIT = 8\n")
    stage(repo, "tests/test_limit.py", "assert True\n")
    rejected(repo, message("runtime", subject="feat(runtime): bound resource use"), "Owners misses tests")
    good = message("runtime, tests", subject="feat(runtime): bound resource use")
    git(repo, "commit", "-m", good)
    original = git(repo, "rev-parse", "HEAD")
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    rejected(repo, message("runtime", subject="feat(runtime): explain resource use"),
             "Owners misses tests", "--amend")
    git(repo, "commit", "--amend", "-m", good.replace("bound", "explain"))
    assert git(repo, "rev-parse", "HEAD^{tree}") == tree

    stage(repo, "docs/new.md", "A reason.\n")
    rejected(repo, message("docs", subject="docs(docs): explain the bound"),
             "Owners misses runtime, tests", "--amend")
    git(repo, "commit", "--amend", "-m", message("docs, runtime, tests",
        subject="feat(runtime): explain resource use"))

    stage(repo, "src/asrai/limit.py", "LIMIT = 16\n")
    rejected(repo, message("runtime", subject="fix(runtime): bound resource use"), "without Fixes")
    trailers = f"Fixes: {original}\n"
    rejected(repo, message("runtime", trailers, "fix(runtime): bound resource use"), "not in Values")
    git(repo, "commit", "-m", message("runtime", trailers + "Values: LIMIT 8->16\n",
                                      "fix(runtime): bound resource use"))

    stage(repo, "src/asrai/limit.py", "LIMIT = 16\n# explanation\n")
    git(repo, "mv", "src/asrai/limit.py", "docs/limit.py")
    rejected(repo, message("docs", subject="refactor(docs): keep policy visible"), "Owners misses runtime")
    git(repo, "commit", "-m", message("docs, runtime", subject="refactor(docs): keep policy visible"))

    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-b", "linked", str(linked))
    stage(linked, ".github/workflows/check.yml", "name: check\n")
    rejected(linked, message("root", subject="ci(root): check every change"), "Owners misses ci")
    git(linked, "commit", "-m", message("ci", subject="ci(ci): check every change"))
    git(linked, "commit", "--amend", "--no-edit")
    git(repo, "merge", "--no-ff", "linked", "-m", message("ci", subject="ci(ci): preserve gate evidence"))

    result = run(repo, sys.executable, "tools/commit_check.py", "--range", f"{root}..HEAD")
    assert result.returncode == 0, result.stdout + result.stderr


def test_commit_checker_rejects_unavailable_evidence_and_malformed_policy(tmp_path):
    repo = tmp_path / "repo"
    setup(repo)
    git(repo, "add", "tools")
    git(repo, "commit", "-m", message("process"))
    head = git(repo, "rev-parse", "HEAD")
    # Newer Git includes symbolic refs in this hook, including checkout/detach updates.
    for row in ("ref:refs/heads/main ref:refs/heads/topic HEAD\n",
                f"ref:refs/heads/main {head} HEAD\n",
                f"{head} ref:refs/heads/main HEAD\n",
                "ref:refs/remotes/origin/main ref:refs/remotes/origin/topic refs/remotes/origin/HEAD\n"):
        result = run(repo, sys.executable, "tools/commit_check.py", "--transaction", input_text=row)
        assert result.returncode == 0, (row, result.stdout + result.stderr)
    unreviewed = git(repo, "commit-tree", "HEAD^{tree}", "-p", head, "-m", "Missing policy")
    result = run(repo, sys.executable, "tools/commit_check.py", "--transaction",
                 input_text=f"ref:refs/heads/main {unreviewed} HEAD\n")
    assert result.returncode != 0 and "no Owners" in result.stdout, result.stdout + result.stderr
    for args in (("--range", "missing..HEAD"), ("--rev", "missing"), ("--rev",),
                 ("missing-message",)):
        result = run(repo, sys.executable, "tools/commit_check.py", *args)
        assert result.returncode != 0, (args, result.stdout + result.stderr)
        assert "Traceback" not in result.stderr, (args, result.stderr)

    stage(repo, "tests/claims.json", '{"limit": 8}\n')
    git(repo, "commit", "-m", message("tests", subject="test(tests): state the resource bound"))
    stage(repo, "tests/claims.json", '{"limit": 16}\n')
    rejected(repo, message("tests", subject="test(tests): raise the resource bound"), "not in Values")
    valid = message("tests", "Values: limit 8->16\n", "test(tests): raise the resource bound")
    for extra, fragment in (("Values: nonsense\n", "Values"),
                            ("Source: missing-revision\n", "Source"),
                            ("Deviation: trust me\n", "Deviation"),
                            ("Owners: tests\n", "duplicate")):
        rejected(repo, valid.replace("Signed-off-by:", extra + "Signed-off-by:"), fragment)
    git(repo, "commit", "-m", valid)

    # ... and the same number change in a resolver's file needs none: adding one tool rewrites the
    # sizes of every wheel in it, and `uv sync --locked` is what actually holds such a file
    lock = 'version = 1\n\n[[package]]\nname = "x"\n\n[package.sdist]\nsize = %d\n'
    stage(repo, "uv.lock", lock % 20538)
    git(repo, "commit", "-m", message("package", subject="build(package): pin the resolved tree"))
    stage(repo, "uv.lock", lock % 16994982)
    git(repo, "commit", "-m", message("package", subject="build(package): add a development tool"))

    shallow = tmp_path / "shallow"
    git(repo, "clone", "--depth", "1", repo.as_uri(), str(shallow))
    result = run(shallow, sys.executable, "tools/commit_check.py", "--rev", "HEAD")
    assert result.returncode != 0 and "full git history" in result.stdout, result.stdout + result.stderr
