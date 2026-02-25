"""Utilities for building and representing f-string format specifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

__all__ = [
    "FormatSpec",
    "build_format_spec",
]


@dataclass
class FormatSpec:
    """Represents the components needed to build a format specification."""

    align: str = ""
    fill: str = ""
    width: int = 0
    comma: bool = False
    underscore: bool = False
    decimals: Optional[int] = None
    type_char: str = ""
    sign: str = ""
    prefix: str = ""
    suffix: str = ""

    # Metadata for generating variations
    value_type: str = "str"  # 'int', 'float', 'str', or 'datetime'
    test_value: float = 0
    datetime_format: str = ""  # For datetime types, stores the strptime format

    def build(self) -> str:
        """Build the format specification string."""
        if self.value_type == "datetime":
            return f'f"{self.prefix}{{variable:{self.datetime_format}}}{self.suffix}"'
        return build_format_spec(
            align=self.align,
            fill=self.fill,
            width=self.width,
            comma=self.comma,
            underscore=self.underscore,
            decimals=self.decimals,
            type_char=self.type_char,
            sign=self.sign,
            prefix=self.prefix,
            suffix=self.suffix,
        )

    def as_tuple(self) -> Tuple[str, str]:
        """Return (value_type, format_spec) tuple for compatibility."""
        return (self.value_type, self.build())


def build_format_spec(
    *,
    align: str = "",
    fill: str = "",
    width: int = 0,
    comma: bool = False,
    underscore: bool = False,
    decimals: Optional[int] = None,
    type_char: str = "",
    sign: str = "",
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Build a format specification string."""
    fill = fill if fill != " " else ""
    width_str = str(width) if width else ""
    comma_str = "," if comma else ""
    underscore_str = "_" if underscore else ""
    decimals_str = f".{decimals}" if decimals is not None else ""

    # Choose separator (underscore takes precedence over comma if both somehow set)
    separator_str = underscore_str or comma_str

    # Special case: integer with separator but no width should omit 'd'
    if type_char == "d" and (comma or underscore) and not width:
        type_char = ""

    if align:
        spec = f"{fill}{align}{sign}{width_str}{separator_str}{decimals_str}{type_char}"
    else:
        spec = f"{sign}{fill}{width_str}{separator_str}{decimals_str}{type_char}"

    if spec:
        return f'f"{prefix}{{variable:{spec}}}{suffix}"'
    return f'f"{prefix}{{variable}}{suffix}"'
