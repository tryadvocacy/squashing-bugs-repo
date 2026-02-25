"""High-level analysis helpers exposed by the fguess package."""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from .datetime_detection import (
    detect_datetime_format,
    has_datetime_structure,
    is_single_numeric_datetime_format,
    split_datetime_literals,
)
from .format_spec import FormatSpec
from .numeric_detection import detect_padding, parse_number_to_spec, split_numeric_literals
from .patterns import HEX_RE, NUMBER_RE, PERCENT_RE, UNPREFIXED_HEX_RE

__all__ = [
    "analyze_number_format",
    "get_test_value",
]


def _as_string_spec(prefix: str = "", suffix: str = "", *, align: str = "", fill: str = "", width: int = 0) -> FormatSpec:
    """Create a string-format spec preserving literal structure."""
    return FormatSpec(
        align=align,
        fill=fill,
        width=width,
        prefix=prefix,
        suffix=suffix,
        value_type="str",
        test_value=0,
    )


def analyze_number_format(sample: str) -> List[Tuple[str, str]]:
    """Analyze a string and return possible format specifications."""
    results: List[Tuple[str, str]] = []

    datetime_format = detect_datetime_format(sample)
    datetime_prefix = ""
    datetime_suffix = ""
    datetime_part = sample

    if not datetime_format:
        prefix, datetime_part, suffix, datetime_format = split_datetime_literals(sample)
        if datetime_format:
            datetime_prefix = prefix or ""
            datetime_suffix = suffix or ""

    if datetime_format:
        try:
            datetime.strptime(datetime_part, datetime_format)
        except ValueError:
            pass

        datetime_spec = FormatSpec(
            value_type="datetime",
            datetime_format=datetime_format,
            prefix=datetime_prefix,
            suffix=datetime_suffix,
            test_value=0,
        )

        is_single_numeric = is_single_numeric_datetime_format(datetime_format)
        datetime_results = [datetime_spec.as_tuple()]
    else:
        datetime_results = []
        is_single_numeric = False

    prefix, number_part, suffix = split_numeric_literals(sample)

    if prefix or suffix:
        numeric_specs = parse_number_to_spec(number_part, prefix=prefix, suffix=suffix)
        numeric_specs.append(_as_string_spec(prefix=prefix, suffix=suffix))
        numeric_results = [spec.as_tuple() for spec in numeric_specs]
    else:
        core, left_pad, right_pad, fill_char = detect_padding(sample)

        if left_pad and right_pad:
            if len(left_pad) == len(right_pad):
                align = "^"
            else:
                spec = _as_string_spec(prefix=left_pad, suffix=right_pad)
                return [spec.as_tuple()]
        elif left_pad:
            align = ">"
        elif right_pad:
            align = "<"
        else:
            align = ""

        width = len(sample) if (left_pad or right_pad) else 0

        if left_pad or right_pad:
            numeric_specs = parse_number_to_spec(core, align=align, fill=fill_char, width=width)
            if align or fill_char != " ":
                numeric_specs.append(_as_string_spec(align=align, fill=fill_char, width=width))
        else:
            numeric_specs = parse_number_to_spec(core, align=align, fill=fill_char, width=width)

        numeric_results = [spec.as_tuple() for spec in numeric_specs]

    if datetime_results and not is_single_numeric:
        if has_datetime_structure(sample):
            results.extend(datetime_results)
            results.extend(numeric_results)
        else:
            results.extend(numeric_results)
            results.extend(datetime_results)
    elif datetime_results and is_single_numeric:
        results.extend(numeric_results)
        results.extend(datetime_results)
    else:
        results.extend(numeric_results)

    return results


def get_test_value(input_str: str, type_name: str):
    """Determine appropriate test value for validation."""
    if type_name == "datetime":
        datetime_format = detect_datetime_format(input_str)
        if datetime_format:
            try:
                return datetime.strptime(input_str, datetime_format)
            except ValueError:
                pass

        prefix, datetime_part, suffix, datetime_format = split_datetime_literals(input_str)
        if datetime_format:
            try:
                return datetime.strptime(datetime_part, datetime_format)
            except ValueError:
                pass

        return datetime(2030, 1, 24, 5, 45, 13)

    prefix, number_part, suffix = split_numeric_literals(input_str)
    if prefix or suffix:
        input_str = number_part

    core, _, _, _ = detect_padding(input_str)
    if core != input_str:
        input_str = core

    if type_name == "str":
        return input_str

    if type_name == "int":
        clean = input_str.replace(",", "").replace("_", "").removeprefix("+")
        if clean and clean.removeprefix("-").isdigit():
            return int(clean)
        if HEX_RE.fullmatch(input_str):
            return int(input_str.removeprefix("0x"), 16)
        if UNPREFIXED_HEX_RE.fullmatch(input_str):
            return int(input_str, 16)
        return 0

    clean = input_str.replace(",", "").replace("_", "").removeprefix("+")
    if PERCENT_RE.fullmatch(input_str):
        clean = clean.removesuffix("%")
        if clean and NUMBER_RE.fullmatch(clean):
            return float(clean) / 100

    if clean and NUMBER_RE.fullmatch(clean):
        return float(clean)
    return 0.0
