"""Format-guessing helpers for f-strings."""

from .analysis import analyze_number_format, get_test_value
from .datetime_detection import detect_datetime_format
from .format_spec import FormatSpec, build_format_spec

__all__ = [
    "FormatSpec",
    "analyze_number_format",
    "build_format_spec",
    "detect_datetime_format",
    "get_test_value",
]

__version__ = "0.0.1"
