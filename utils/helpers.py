"""
Shared utility helpers used across the toolkit.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


def slugify(text: str) -> str:
    """
    Convert text to a lowercase slug (URL-safe, filesystem-safe string).

    Example:
        >>> slugify("Hello, World!")
        'hello-world'
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp *value* between *minimum* and *maximum* (inclusive)."""
    return max(minimum, min(value, maximum))


def truncate(text: str, max_length: int = 80, suffix: str = "…") -> str:
    """Shorten *text* to *max_length* characters, appending *suffix* if cut."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def chunk(lst: list[Any], size: int) -> list[list[Any]]:
    """
    Split *lst* into consecutive chunks of *size*.

    Example:
        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    if size < 1:
        raise ValueError("Chunk size must be at least 1.")
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def flatten(nested: list[Any]) -> list[Any]:
    """Recursively flatten a nested list."""
    result: list[Any] = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
