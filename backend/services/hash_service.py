"""
SHA-256 integrity processing (FR-16 through FR-23).

Python generates the hash from exact file bytes.
SQLite only stores the resulting digest — it never computes it.
"""

import hashlib
import re
from pathlib import Path

CHUNK_SIZE = 8192  # NFR-03: stream, don't load entire file
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def compute_sha256(file_path: str | Path) -> str:
    """
    Compute SHA-256 digest of a file using chunked binary reading.

    Returns:
        Lowercase 64-character hexadecimal digest string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path is a directory.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {path}")

    sha256 = hashlib.sha256()  # FR-17
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):  # FR-18
            sha256.update(chunk)

    digest = sha256.hexdigest()  # FR-19: lowercase hex, 64 chars
    return digest


def is_valid_sha256(value: str) -> bool:
    """Check whether a string is a valid SHA-256 hex digest."""
    return bool(SHA256_PATTERN.match(value))
