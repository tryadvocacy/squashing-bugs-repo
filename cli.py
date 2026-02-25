"""Command-line interface for the fguess package."""

from __future__ import annotations

from typing import Iterable, Optional

from .analysis import analyze_number_format, get_test_value

PROMPT = "Enter a formatted string (or 'quit' to exit):"
SEPARATOR = "-" * 40
LOOP_SEPARATOR = "=" * 40
EXIT_WORDS = {"quit", "exit", "q"}


def _render_analysis(sample: str) -> Iterable[str]:
    """Yield lines describing the inferred format specifications."""
    yield f"\nInput: '{sample}'"
    yield SEPARATOR

    results = analyze_number_format(sample)
    if not results:
        yield "No format specifications found"
        return

    seen = set()
    for type_name, format_spec in results:
        if (type_name, format_spec) in seen:
            continue
        seen.add((type_name, format_spec))

        test_value = get_test_value(sample, type_name)
        yield f"{type_name:8} → {format_spec}"
        yield f"           (e.g., variable = {repr(test_value)})"
        yield ""


def main(argv: Optional[Iterable[str]] = None) -> int:
    """Run the CLI. When a value is supplied, analyse it once; otherwise loop."""
    args = list(argv or [])
    if args:
        for line in _render_analysis(args[0]):
            print(line)
        return 0

    print(PROMPT)
    while True:
        try:
            sample = input().strip()
        except EOFError:
            print()
            return 0

        if sample.lower() in EXIT_WORDS:
            return 0

        for line in _render_analysis(sample):
            print(line)

        print("\n" + LOOP_SEPARATOR)
        print(PROMPT)


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
