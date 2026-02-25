# AGENTS

## Working With These Exercises
- Run any package from the repository root with `python -m <package>`.
- Execute that package's tests with `python -m unittest discover -s <package>`.
- Tests live under `<package>/tests`; lean on them to reproduce bugs and to add coverage when you create fixes.
- Several CLIs are interactive: pass sample input as an argument when you want non-interactive runs.

## Exercises

### dramatic
- Run dramatic Python sessions; can patch stdout/stderr with `--max-drama`, undo via `--min-drama`, control speed with `--speed`, or run modules/files with `-m`/path.
- Entry point in `dramatic/cli.py`; supporting behaviour in `dramatic/io.py`, `dramatic/patching.py`, and helpers in `dramatic/tests/`.
- Tests: `python -m unittest discover -s dramatic`.
- Quick checks: `python -m dramatic --help`, `python -m dramatic example.py`, or `python -m dramatic -m mimetypes -e text/markdown`.

### fguess
- Infers f-string format specs for numeric, datetime, and mixed strings.
- CLI lives in `fguess/cli.py`; inference logic spans `fguess/analysis.py`, `fguess/numeric_detection.py`, `fguess/datetime_detection.py`, and `fguess/format_spec.py`.
- Tests: `python -m unittest discover -s fguess`.
- Quick checks: `python -m fguess "1,234.56"` or launch without arguments for the interactive prompt.

### strptime
- Guesses `datetime.strptime` format strings from sample input, with bold prompts when no argument is supplied.
- Core CLI in `strptime/cli.py`; detection logic in `strptime/detection.py`, pattern data in `strptime/patterns.py`, and constants in `strptime/constants.py`.
- Tests: `python -m unittest discover -s strptime`.
- Quick checks: `python -m strptime "2030-01-24 05:45"` or run without args to exercise `prompt_for_date()`.

### undataclass
- Transforms `@dataclass` classes into equivalent regular classes by editing the AST.
- CLI in `undataclass/cli.py`; transformation pipeline in `undataclass/transform.py` with helpers in `undataclass/decorators.py`, `undataclass/fields.py`, and `undataclass/codegen.py`.
- Tests: `python -m unittest discover -s undataclass`; compare inputs and outputs under `undataclass/tests/files/`.
- Quick checks: `python -m undataclass undataclass/tests/files/before/simple.py`.

### vtt2txt
- Converts WebVTT transcripts to plain text, emitting one sentence per line and stripping numbering, timestamps, and tags.
- CLI in `vtt2txt/__main__.py`; text processing lives in `vtt2txt/__init__.py`.
- Tests: `python -m unittest discover -s vtt2txt`.
- Quick checks: `python -m vtt2txt python314.vtt` or try the longer `python314-youtube.vtt`.

## Suggested Agent Flow
- Start by running the package's tests to capture current failures (`python -m unittest discover -s <package>`).
- Reproduce the issue through its CLI when possible to observe user-facing behaviour.
- Add or update tests in the package's `tests/` directory before fixing bugs.
- After fixing bugs re-run the full suite for that package before wrapping up.
