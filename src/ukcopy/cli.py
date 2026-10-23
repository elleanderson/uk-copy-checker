"""Command-line interface: ukcopy check docs/ README.md"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from . import __version__
from .checker import Config, check_path, check_text, iter_files
from .rules import RULES


def _print_text(issues, files_checked: int) -> None:
    for i in issues:
        print(f"{i.path}:{i.line}:{i.column}  {i.rule:<22} {i.message}")
        if i.excerpt:
            print(f"{'':>8}…{i.excerpt}…")
    counts = Counter(i.rule for i in issues)
    summary = ", ".join(f"{n} {r}" for r, n in counts.most_common()) or "nothing to fix"
    print(f"\n{len(issues)} issue{'s' if len(issues) != 1 else ''} in {files_checked} file{'s' if files_checked != 1 else ''}: {summary}")


def _print_github(issues) -> None:
    # GitHub Actions workflow commands become inline annotations on pull requests
    for i in issues:
        msg = i.message.replace("%", "%25").replace("\n", "%0A")
        print(f"::warning file={i.path},line={i.line},col={i.column},title=ukcopy {i.rule}::{msg}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ukcopy", description="Check writing against a UK English house style.")
    p.add_argument("--version", action="version", version=f"ukcopy {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="check files or folders")
    c.add_argument("paths", nargs="*", default=["."], help="files or folders (Markdown, text or HTML)")
    c.add_argument("--format", choices=["text", "json", "github"], default="text")
    c.add_argument("--disable", action="append", default=[], metavar="RULE", help="turn a rule off (repeatable)")
    c.add_argument("--max-sentence-words", type=int)
    c.add_argument("--stdin", action="store_true", help="read Markdown from standard input")
    c.add_argument("--no-fail", action="store_true", help="always exit 0, even when issues are found")

    sub.add_parser("rules", help="list the rules")

    a = p.parse_args(argv)
    if a.cmd == "rules":
        for r in RULES.values():
            print(f"{r.name:<22} {r.summary}")
        return 0

    cfg = Config.load()
    cfg.disabled |= set(a.disable)
    if a.max_sentence_words:
        cfg.max_sentence_words = a.max_sentence_words
    unknown = cfg.disabled - set(RULES)
    if unknown:
        p.error(f"unknown rule(s): {', '.join(sorted(unknown))}. Run 'ukcopy rules' to see them.")

    if a.stdin:
        issues, n = check_text(sys.stdin.read(), "md", cfg, "<stdin>"), 1
    else:
        files = list(iter_files(a.paths))
        issues = [i for f in files for i in check_path(Path(f), cfg)]
        n = len(files)

    if a.format == "json":
        print(json.dumps([i.__dict__ for i in issues], indent=2, ensure_ascii=False))
    elif a.format == "github":
        _print_github(issues)
        _print_text(issues, n)
    else:
        _print_text(issues, n)
    return 0 if (a.no_fail or not issues) else 1


if __name__ == "__main__":
    sys.exit(main())
