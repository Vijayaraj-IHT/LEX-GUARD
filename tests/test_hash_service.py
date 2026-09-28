"""Tests for SHA-256 hash service."""

import tempfile
from pathlib import Path

import pytest

from backend.services.hash_service import compute_sha256, is_valid_sha256


def test_known_hash():
    """SHA-256 of 'hello\\n' is well-known."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello\n")
        f.flush()
        digest = compute_sha256(f.name)
    # echo -n "hello\n" | sha256sum
    assert digest == "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03"
    Path(f.name).unlink()


def test_changed_file_different_hash():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f1:
        f1.write("version 1")
        f1.flush()
        h1 = compute_sha256(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f2:
        f2.write("version 2")
        f2.flush()
        h2 = compute_sha256(f2.name)

    assert h1 != h2
    Path(f1.name).unlink()
    Path(f2.name).unlink()


def test_valid_sha256_format():
    assert is_valid_sha256("a" * 64) is True
    assert is_valid_sha256("A" * 64) is False  # uppercase
    assert is_valid_sha256("a" * 63) is False  # too short


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        compute_sha256("/nonexistent/path/file.pdf")
