"""Datetime detection utilities for fguess."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional, Tuple

import strptime

from .patterns import ISO_DATETIME_MICROSECOND_RE

__all__ = [
    "detect_datetime_format",
    "has_datetime_structure",
    "is_single_numeric_datetime_format",
    "split_datetime_literals",
]


def detect_datetime_format(text: str) -> Optional[str]:
    """Detect datetime format from text string."""
    try:
        detected = strptime.detect_format(text)
    except ValueError:
        detected = None

    if (not detected or "%f" not in detected) and ISO_DATETIME_MICROSECOND_RE.match(text):
        try:
            datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            pass
        else:
            return "%Y-%m-%dT%H:%M:%S.%f"

    return detected


def is_single_numeric_datetime_format(datetime_format: str) -> bool:
    """Check if datetime format is just a single numeric component like %d or %Y."""
    single_numeric_formats = {"%d", "%m", "%y", "%Y", "%H", "%I", "%M", "%S", "%j"}
    return datetime_format in single_numeric_formats


def has_datetime_structure(text: str) -> bool:
    """Check if string has structure that suggests datetime (spaces, dashes, colons, etc)."""
    datetime_separators = {" ", "-", "/", ":", "T", "+"}
    return any(sep in text for sep in datetime_separators)


def split_datetime_literals(text: str) -> Tuple[Optional[str], str, Optional[str], Optional[str]]:
    """Try to find datetime parts within a string with literals."""
    datetime_patterns = [
        re.compile(r"(.*?)(\d{4}-\d{2}-\d{2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?(?:\s*[AP]M)?)(.*)", re.IGNORECASE),
        re.compile(r"(.*?)(\d{1,2}/\d{1,2}/\d{2,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?\s*[AP]M?)?)(.*)", re.IGNORECASE),
        re.compile(r"(.*?)(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)(.*)", re.IGNORECASE),
        re.compile(r"(.*?)(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,?\s+\d{4})?(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?(?:\s*[AP]M)?)(.*)", re.IGNORECASE),
        re.compile(r"(.*?)(\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:\s+\d{4})?(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?(?:\s*[AP]M)?)(.*)", re.IGNORECASE),
        re.compile(r"(.*?)(\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b)(.*)", re.IGNORECASE),
    ]

    for pattern in datetime_patterns:
        match = pattern.fullmatch(text)
        if match:
            prefix, datetime_part, suffix = match.groups()
            detected = detect_datetime_format(datetime_part.strip())
            if detected:
                return prefix, datetime_part.strip(), suffix, detected

    return None, text, None, None
