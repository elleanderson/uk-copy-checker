# Contributing

Thank you for helping. Small, careful improvements are the most useful kind.

## Good First Contributions

- A US spelling that's missing from `src/ukcopy/spelling.py`, with its British form
- A stock phrase for the `ai-phrases` rule, with a plainer alternative
- A false alarm, such as a phrasal verb wrongly flagged as a stranded preposition

## How to Make a Change

1. Fork the repository and create a branch.
2. Install it with `pip install -e ".[dev]"`.
3. Add a test in `tests/` that shows the problem, then make it pass.
4. Run `pytest -q` and `ukcopy check README.md CONTRIBUTING.md` before you open a pull request.

## Style

Every word in this repository passes its own checker. Please keep it that way.

## Behaviour

Be kind, assume good intent and keep feedback about the work. Anyone who makes the space unwelcoming will be asked to leave it.
