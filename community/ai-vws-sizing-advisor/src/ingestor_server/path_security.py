# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Path validation helpers to prevent path-traversal on document uploads."""

from __future__ import annotations

import os
import re
from pathlib import Path

# Upload root for ingested files. Never write outside this directory.
UPLOAD_ROOT = Path(os.getenv("INGESTOR_UPLOAD_ROOT", "/tmp-data/uploaded_files")).resolve()

# Collection names are used as directory segments — keep them strict.
_SAFE_COLLECTION_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]{0,254}$")


class UnsafePathError(ValueError):
    """Raised when a user-supplied path component fails validation."""


def validate_safe_collection_name(name: str | None, field: str = "collection_name") -> str:
    """Reject empty, traversal, and separator-bearing collection names."""
    if name is None:
        raise UnsafePathError(f"Invalid {field}: missing value")

    if "\x00" in name or "/" in name or "\\" in name:
        raise UnsafePathError(f"Invalid {field}: path separators not allowed")

    candidate = os.path.basename(name.strip())
    if not candidate or candidate in {".", ".."} or not _SAFE_COLLECTION_RE.fullmatch(candidate):
        raise UnsafePathError(
            f"Invalid {field}: must be 1-255 characters, start with a letter, digit, or '_', "
            "and contain only letters, digits, '.', '_' or '-'"
        )
    return candidate


def validate_safe_filename(name: str | None, field: str = "filename") -> str:
    """
    Sanitize an upload filename to a single path segment.

    Allows common document name characters (spaces, parentheses, etc.) but
    rejects traversal sequences and path separators.
    """
    if name is None:
        raise UnsafePathError(f"Invalid {field}: missing value")

    if "\x00" in name:
        raise UnsafePathError(f"Invalid {field}: null bytes not allowed")

    candidate = os.path.basename(name.strip())
    if not candidate or candidate in {".", ".."}:
        raise UnsafePathError(f"Invalid {field}: empty or traversal name")

    # Defense in depth if basename behavior differs across platforms
    if "/" in candidate or "\\" in candidate:
        raise UnsafePathError(f"Invalid {field}: path separators not allowed")

    if len(candidate) > 255:
        raise UnsafePathError(f"Invalid {field}: exceeds 255 characters")

    return candidate


def validate_safe_name(name: str | None, field: str = "name") -> str:
    """Validate a collection-like or filename identifier based on field name."""
    if field in {"filename", "document_name"}:
        return validate_safe_filename(name, field)
    return validate_safe_collection_name(name, field)


def safe_collection_dir(collection_name: str) -> Path:
    """Return a directory under UPLOAD_ROOT for the given collection."""
    safe_collection = validate_safe_collection_name(collection_name, "collection_name")
    collection_dir = (UPLOAD_ROOT / safe_collection).resolve()
    if not collection_dir.is_relative_to(UPLOAD_ROOT):
        raise UnsafePathError("Invalid collection_name: path traversal detected")
    return collection_dir


def safe_upload_file_path(collection_name: str, filename: str | None) -> tuple[Path, str]:
    """
    Build a write destination confined to UPLOAD_ROOT/<collection>/<filename>.

    Returns:
        (absolute_file_path, sanitized_filename)
    """
    collection_dir = safe_collection_dir(collection_name)
    safe_filename = validate_safe_filename(filename, "filename")
    file_path = (collection_dir / safe_filename).resolve()
    if not file_path.is_relative_to(UPLOAD_ROOT):
        raise UnsafePathError("Invalid filename: path traversal detected")
    return file_path, safe_filename
