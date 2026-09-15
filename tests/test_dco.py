import subprocess

import pytest

from check_dco import DCOError, check


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo, name, message):
    (repo / name).write_text(name)
    _git(repo, "add", name)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def test_dco_checks_only_new_commits_and_requires_a_valid_trailer(tmp_path):
    """Protect the adoption boundary so unsigned new commits cannot enter through CI."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Test Author")
    _git(repo, "config", "user.email", "author@example.com")

    base = _commit(repo, "base", "Unsigned base")
    _commit(repo, "old", "Old unsigned commit")
    grandfather = _commit(repo, "grandfather", "Grandfathered unsigned commit")
    valid = _commit(
        repo,
        "valid",
        "Adopt DCO\n\nSigned-off-by: Test Author <author@example.com>",
    )
    check(repo, base, valid, grandfather)

    cases = [
        ("unsigned", "New unsigned commit"),
        (
            "body-only",
            "Mention a signoff\n\nSigned-off-by: Test Author <author@example.com>\n\nStill body text",
        ),
        ("malformed", "Malformed signoff\n\nSigned-off-by: Test Author"),
    ]
    for name, message in cases:
        _git(repo, "checkout", "-B", name, valid)
        head = _commit(repo, name, message)
        with pytest.raises(DCOError, match=head):
            check(repo, base, head, grandfather)

    _git(repo, "checkout", "-B", "signed", valid)
    signed = _commit(
        repo,
        "signed",
        "Valid signoff\n\nSigned-off-by: Another Person <person@example.org>",
    )
    check(repo, base, signed, grandfather)

    with pytest.raises(DCOError, match="missing-base"):
        check(repo, "missing-base", signed, grandfather)

    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", "signed", repo.as_uri(), shallow],
        check=True,
        capture_output=True,
        text=True,
    )
    with pytest.raises(DCOError, match="full git history is required"):
        check(shallow, signed, signed, signed)
