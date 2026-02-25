"""Helpers for parsing numeric strings into candidate format specs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .format_spec import FormatSpec
from .patterns import (
    FULL_HEX_RE,
    FULL_NUMBER_RE,
    FULL_PERCENT_RE,
    FULL_THOUSANDS_RE,
    FULL_UNDERSCORE_RE,
    FULL_UNPREFIXED_HEX_RE,
    HEX_RE,
    NUMBER_RE,
    PAD_CHARS,
    PERCENT_RE,
    THOUSANDS_RE,
    UNDERSCORE_RE,
    UNPREFIXED_HEX_RE,
    ZERO_PADDED_RE,
)

__all__ = [
    "NumberParts",
    "count_decimals",
    "detect_padding",
    "parse_number_to_spec",
    "split_numeric_literals",
]


@dataclass
class NumberParts:
    """Decomposed representation of a numeric segment."""

    prefix: str
    num: str
    suffix: str

    def __iter__(self):
        return iter((self.prefix, self.num, self.suffix))


def is_padding(text: str) -> bool:
    """Check if text represents padding characters."""
    return len(text) > 0 and len(set(text)) == 1 and text[0] in PAD_CHARS


def count_decimals(number_string: str) -> int:
    """Return number of decimals in given numeric string."""
    return len(number_string.split(".")[1]) if "." in number_string else 0


def split_numeric_literals(s: str) -> NumberParts:
    """Split a string into prefix literals, numeric part, and suffix literals."""
    if match := FULL_HEX_RE.fullmatch(s):
        return NumberParts(*match.groups())

    if match := FULL_PERCENT_RE.fullmatch(s):
        prefix, num, suffix = match.groups()
        left_pad = is_padding(prefix)
        right_pad = is_padding(suffix)
        if (left_pad or right_pad) and (left_pad != right_pad or prefix[0] == suffix[0]):
            return NumberParts("", s, "")
        return NumberParts(prefix, num, suffix)

    if match := FULL_UNPREFIXED_HEX_RE.fullmatch(s):
        prefix, num, suffix = match.groups()
        left_pad = is_padding(prefix)
        right_pad = is_padding(suffix)
        if not ((left_pad and not right_pad) or (right_pad and not left_pad)):
            return NumberParts(prefix, num, suffix)

    for regex in [FULL_THOUSANDS_RE, FULL_UNDERSCORE_RE, FULL_NUMBER_RE]:
        if match := regex.fullmatch(s):
            prefix, num, suffix = match.groups()
            left_pad = is_padding(prefix)
            right_pad = is_padding(suffix)
            if (left_pad or right_pad) and (left_pad != right_pad or prefix[0] == suffix[0]):
                return NumberParts("", s, "")
            return NumberParts(prefix, num, suffix)

    return NumberParts("", s, "")


def detect_padding(s: str) -> Tuple[str, str, str, str]:
    """Detect consistent padding in a string."""
    for char in PAD_CHARS:
        left = len(s) - len(s.lstrip(char))
        right = len(s.rstrip(char))
        left_pad, core, right_pad = s[:left], s[left:right], s[right:]
        if (left_pad or right_pad) and core:
            return core, left_pad, right_pad, char
    return s, "", "", " "


def parse_number_to_spec(
    s: str,
    *,
    prefix: str = "",
    suffix: str = "",
    align: str = "",
    fill: str = "",
    width: int = 0,
) -> List[FormatSpec]:
    """Parse a string as a number and return FormatSpec objects."""

    if HEX_RE.fullmatch(s):
        value = int(s.removeprefix("0x"), 16)
        is_padded = s.startswith("0x0")
        return [
            FormatSpec(
                fill="0" if is_padded else "",
                width=len(s) if is_padded else 0,
                type_char="x",
                sign="#",
                prefix=prefix,
                suffix=suffix,
                value_type="int",
                test_value=value,
            )
        ]

    if UNPREFIXED_HEX_RE.fullmatch(s):
        value = int(s, 16)
        hex_char = "X" if s.isupper() else "x"
        is_padded = len(s) > 1 and s[0] == "0"
        return [
            FormatSpec(
                fill="0" if is_padded else "",
                width=len(s) if is_padded else 0,
                type_char=hex_char,
                prefix=prefix,
                suffix=suffix,
                value_type="int",
                test_value=value,
            )
        ]

    if PERCENT_RE.fullmatch(s):
        num = s.removesuffix("%")
        value = float(num) / 100
        decimals = count_decimals(num)
        has_sign = num.startswith("+")
        return [
            FormatSpec(
                align=align,
                fill=fill,
                width=width,
                sign="+" if has_sign else "",
                decimals=decimals,
                type_char="%",
                prefix=prefix,
                suffix=suffix,
                value_type="float",
                test_value=value,
            )
        ]

    if ZERO_PADDED_RE.fullmatch(s.removeprefix("+")):
        width_val = len(s)
        decimals = count_decimals(s)
        has_sign = s.startswith("+")
        value = float(s) if decimals else int(s)

        results: List[FormatSpec] = []
        if not decimals:
            results.append(
                FormatSpec(
                    fill="0",
                    width=width_val,
                    type_char="d",
                    sign="+" if has_sign else "",
                    prefix=prefix,
                    suffix=suffix,
                    value_type="int",
                    test_value=abs(value),
                )
            )

        results.append(
            FormatSpec(
                fill="0",
                width=width_val,
                decimals=decimals,
                type_char="f",
                sign="+" if has_sign else "",
                prefix=prefix,
                suffix=suffix,
                value_type="float",
                test_value=abs(float(value)),
            )
        )
        return results

    clean = s.replace(",", "").replace("_", "")
    if NUMBER_RE.fullmatch(clean):
        has_comma = THOUSANDS_RE.fullmatch(s)
        has_underscore = UNDERSCORE_RE.fullmatch(s)
        decimals = count_decimals(clean)
        has_sign = s.startswith("+")
        sign = "+" if has_sign else ""

        if "." in clean and decimals == 0:
            clean_for_int = clean.rstrip(".")
            value = int(clean_for_int) if clean_for_int else 0
            float_value = float(clean)
        else:
            value = float(clean) if decimals else int(clean)
            float_value = float(clean)

        results = []
        if not decimals and (align or has_comma or has_underscore or sign or fill.strip()):
            results.append(
                FormatSpec(
                    align=align,
                    fill=fill,
                    width=width,
                    comma=bool(has_comma),
                    underscore=bool(has_underscore),
                    type_char="d",
                    sign=sign,
                    prefix=prefix,
                    suffix=suffix,
                    value_type="int",
                    test_value=abs(int(value)),
                )
            )

        float_spec = FormatSpec(
            align=align,
            fill=fill,
            width=width,
            comma=bool(has_comma),
            underscore=bool(has_underscore),
            decimals=decimals,
            type_char="f",
            sign=sign,
            prefix=prefix,
            suffix=suffix,
            value_type="float",
            test_value=abs(float_value),
        )
        if not decimals and (has_comma or has_underscore):
            results.insert(0, float_spec)
        else:
            results.append(float_spec)

        return results

    return []
