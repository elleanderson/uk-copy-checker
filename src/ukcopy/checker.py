"""Turn files into lines of prose, run the rules and collect issues."""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

from .rules import RULES, Issue

DISABLE_LINE = "ukcopy-disable-line"
DISABLE_START = "ukcopy-disable"
DISABLE_END = "ukcopy-enable"


@dataclass
class Config:
    disabled: set[str] = field(default_factory=set)
    max_sentence_words: int = 30
    allow: set[str] = field(default_factory=set)  # exact phrases to ignore wherever they appear

    @classmethod
    def load(cls, start: Path | None = None) -> "Config":
        here = (start or Path.cwd()).resolve()
        for folder in [here, *here.parents]:
            for name in (".ukcopy.toml", "pyproject.toml"):
                f = folder / name
                if f.is_file():
                    data = tomllib.loads(f.read_text(encoding="utf-8"))
                    section = data.get("tool", {}).get("ukcopy") if name == "pyproject.toml" else data
                    if section:
                        return cls(
                            disabled=set(section.get("disable", [])),
                            max_sentence_words=int(section.get("max-sentence-words", 30)),
                            allow={a.lower() for a in section.get("allow", [])},
                        )
        return cls()


def _mask_inline_code(line: str) -> str:
    # stand in a neutral word, so "install it with `pip`." doesn't look like it ends on "with"
    return re.sub(r"`[^`]*`", lambda m: "code" + " " * (len(m.group(0)) - 4) if len(m.group(0)) >= 4 else "x" * len(m.group(0)), line)


def _mask_links(line: str) -> str:
    # keep the link text, hide the URL
    line = re.sub(r"\]\([^)]*\)", lambda m: "]" + " " * (len(m.group(0)) - 1), line)
    return re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), line)


def prose_lines_markdown(text: str):
    """Yield (line_no, text, is_heading) for prose in Markdown, skipping code and front matter."""
    in_code = in_front = False
    disabled = False
    for i, raw in enumerate(text.splitlines(), start=1):
        s = raw.strip()
        if i == 1 and s == "---":
            in_front = True
            continue
        if in_front:
            in_front = s != "---"
            continue
        if s.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or raw.startswith("    "):
            continue
        if DISABLE_END in s:
            disabled = False
            continue
        if DISABLE_START in s and DISABLE_LINE not in s:
            disabled = True
            continue
        if disabled or DISABLE_LINE in s:
            continue
        if s.startswith(("<", "|---", "| ---", "![")):
            # raw HTML rows, table rules and images are not prose
            if not s.startswith("<p"):
                continue
        is_heading = bool(re.match(r"#{1,6}\s", s))
        line = re.sub(r"^#{1,6}\s+", "", raw) if is_heading else raw
        line = _mask_links(_mask_inline_code(line))
        line = re.sub(r"<[^>]+>", lambda m: " " * len(m.group(0)), line)
        yield i, line, is_heading


def prose_lines_html(text: str):
    """Yield prose lines from HTML, ignoring scripts, styles, code and tags."""
    blank = lambda m: "\n" * m.group(0).count("\n")
    text = re.sub(r"<(script|style|pre|code|svg)\b.*?</\1>", blank, text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    for i, raw in enumerate(text.splitlines(), start=1):
        is_heading = bool(re.search(r"<h[1-6][\s>]", raw, re.I))
        line = html.unescape(re.sub(r"<[^>]+>", " ", raw))
        if line.strip() and DISABLE_LINE not in raw:
            yield i, line, is_heading


def check_text(text: str, kind: str = "md", config: Config | None = None, path: str = "") -> list[Issue]:
    cfg = config or Config()
    lines = prose_lines_html(text) if kind == "html" else prose_lines_markdown(text)
    issues: list[Issue] = []
    for line_no, line, is_heading in lines:
        for name, rule in RULES.items():
            if name in cfg.disabled:
                continue
            for issue in rule.check(line, line_no, is_heading=is_heading, max_words=cfg.max_sentence_words):
                if cfg.allow and any(a in issue.excerpt.lower() for a in cfg.allow):
                    continue
                issues.append(replace(issue, path=path))
    return issues


KINDS = {".md": "md", ".markdown": "md", ".txt": "md", ".html": "html", ".htm": "html"}


def check_path(path: Path, config: Config | None = None) -> list[Issue]:
    kind = KINDS.get(path.suffix.lower())
    if not kind:
        return []
    return check_text(path.read_text(encoding="utf-8", errors="replace"), kind, config, str(path))


def iter_files(targets: list[str]):
    for t in targets:
        p = Path(t)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.suffix.lower() in KINDS and not any(part.startswith(".") or part in {"node_modules", "dist", "build"} for part in f.parts):
                    yield f
        elif p.is_file():
            yield p
