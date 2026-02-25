"""Regular expression helpers used by the fguess package."""

from __future__ import annotations

import re

__all__ = [
    "HEX_RE",
    "UNPREFIXED_HEX_RE",
    "PERCENT_RE",
    "ZERO_PADDED_RE",
    "THOUSANDS_RE",
    "UNDERSCORE_RE",
    "NUMBER_RE",
    "FULL_HEX_RE",
    "FULL_UNPREFIXED_HEX_RE",
    "FULL_PERCENT_RE",
    "FULL_THOUSANDS_RE",
    "FULL_UNDERSCORE_RE",
    "FULL_NUMBER_RE",
    "ISO_DATETIME_MICROSECOND_RE",
    "PAD_CHARS",
]

HEX_RE = re.compile(r"0[xX][0-9a-fA-F]+")
UNPREFIXED_HEX_RE = re.compile(r"[0-9]*[a-fA-F]+[0-9]*")
PERCENT_RE = re.compile(r"[+-]?\d+\.?\d*%")
ZERO_PADDED_RE = re.compile(r"0+\d+\.?\d*")
THOUSANDS_RE = re.compile(r"[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?")
UNDERSCORE_RE = re.compile(r"[+-]?\d{1,3}(?:_\d{3})+(?:\.\d+)?")
NUMBER_RE = re.compile(r"[+-]?\d+\.?\d*")

FULL_HEX_RE = re.compile(rf"(.*?)({HEX_RE.pattern})(.*)")
FULL_UNPREFIXED_HEX_RE = re.compile(rf"()({UNPREFIXED_HEX_RE.pattern})()")
FULL_PERCENT_RE = re.compile(rf"(.*?)({PERCENT_RE.pattern})(.*)")
FULL_THOUSANDS_RE = re.compile(rf"(.*?)({THOUSANDS_RE.pattern})(.*)")
FULL_UNDERSCORE_RE = re.compile(rf"(.*?)({UNDERSCORE_RE.pattern})(.*)")
FULL_NUMBER_RE = re.compile(rf"(.*?)({NUMBER_RE.pattern})(.*)")

ISO_DATETIME_MICROSECOND_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+$")

PAD_CHARS = " _*"
