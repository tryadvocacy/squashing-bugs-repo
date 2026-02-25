"""Module entrypoint for ``python -m fguess``."""

from .cli import main


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
