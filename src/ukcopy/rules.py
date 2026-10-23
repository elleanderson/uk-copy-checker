"""The rules. Each rule is a small function that takes one line of prose and
yields Issues. Rules never see code blocks, HTML tags, scripts or front matter."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterator

from .spelling import US_TO_UK


@dataclass(frozen=True)
class Issue:
    rule: str
    line: int
    column: int
    message: str
    excerpt: str
    path: str = ""


@dataclass(frozen=True)
class Rule:
    name: str
    summary: str
    check: Callable[..., Iterator[Issue]]
    default: bool = True


def _issue(rule: str, line_no: int, m: re.Match | None, text: str, message: str, col: int | None = None) -> Issue:
    start = m.start() if m else (col or 0)
    lo, hi = max(0, start - 25), min(len(text), (m.end() if m else start) + 25)
    return Issue(rule, line_no, start + 1, message, text[lo:hi].strip())


# ---------------------------------------------------------------- punctuation

EM_DASH = re.compile("—|(?<=\\w)--(?=\\w)|\\s–\\s")


def em_dash(text: str, line_no: int, **_) -> Iterator[Issue]:
    for m in EM_DASH.finditer(text):
        yield _issue("em-dash", line_no, m, text, "Avoid dashes as punctuation. Use a full stop, comma, colon or brackets.")


OXFORD = re.compile(r"\b[\w'’-]+, (?:[\w'’-]+ ){0,3}[\w'’-]+, (?:and|or) (\w+)", re.IGNORECASE)
# "clear, warm writing, and I help" joins two clauses, so that comma is fine
CLAUSE_STARTERS = {"i", "we", "you", "they", "he", "she", "it", "this", "that", "there", "then", "so"}


def oxford_comma(text: str, line_no: int, **_) -> Iterator[Issue]:
    for m in OXFORD.finditer(text):
        if m.group(1).lower() in CLAUSE_STARTERS:
            continue
        comma = text.rfind(",", m.start(), m.end())
        yield _issue("oxford-comma", line_no, None, text, "Drop the comma before the final \"and\" or \"or\".", col=comma)


def exclamation(text: str, line_no: int, **_) -> Iterator[Issue]:
    for m in re.finditer(r"(?<=\w)!+", text):
        yield _issue("exclamation", line_no, m, text, "Let the words carry the energy. Use a full stop.")


# ---------------------------------------------------------------- grammar and style

PREPOSITIONS = {"of", "for", "to", "with", "about", "on", "at", "from", "in", "into", "upon", "within", "by", "through"}
PHRASAL_OK = {
    "set up", "show up", "turn up", "give up", "keep up", "catch up", "back up", "sign up", "follow up",
    "open up", "speak up", "step up", "start up", "kick in", "log in", "sign in", "check in", "fit in",
    "join in", "hand in", "carry on", "move on", "hold on", "take on", "go on", "come on", "log on",
    "switch on", "build on", "turn on", "lean on", "count on", "rely on", "dawn on", "get on", "plug in",
    "opt in", "drop in", "settle in", "sink in", "break through", "follow through", "come through",
    "get through", "see through", "pull through", "slips through", "slip through", "stand by", "come by", "get by", "drop by", "pass by",
    "put up with", "look forward to", "opt out of",
}
SENTENCE_END = re.compile(r"[^.!?]+[.!?]")


def stranded_preposition(text: str, line_no: int, **_) -> Iterator[Issue]:
    for m in SENTENCE_END.finditer(text):
        sentence = m.group(0)
        words = [w.lower().strip("'’\"“”()") for w in re.findall(r"[A-Za-z'’]+", sentence)]
        if len(words) < 3 or words[-1] not in PREPOSITIONS:
            continue
        if f"{words[-2]} {words[-1]}" in PHRASAL_OK or " ".join(words[-3:]) in PHRASAL_OK:
            continue
        yield _issue("stranded-preposition", line_no, m, text,
                     f"Sentence ends on \"{words[-1]}\". Rewrite so it ends on a stronger word.")


def sentence_length(text: str, line_no: int, max_words: int = 30, **_) -> Iterator[Issue]:
    for m in SENTENCE_END.finditer(text):
        n = len(re.findall(r"\b[\w'’-]+\b", m.group(0)))
        if n > max_words:
            yield _issue("sentence-length", line_no, m, text, f"Long sentence ({n} words). Aim for {max_words} or fewer.")


# ---------------------------------------------------------------- vocabulary

def _inflect(word: str) -> str:
    if " " in word:
        return rf"\b{re.escape(word)}s?\b"
    if word.endswith("e"):
        return rf"\b{re.escape(word[:-1])}(?:e|es|ed|er|ers|ing)\b"
    return rf"\b{re.escape(word)}(?:s|ed|ing|er|ers|es)?\b"


US_PATTERN = re.compile("|".join(f"(?P<w{i}>{_inflect(w)})" for i, w in enumerate(US_TO_UK)), re.IGNORECASE)
US_KEYS = list(US_TO_UK)


def _british_form(found: str, us: str) -> str:
    """Carry the inflection across: "colors" becomes "colours", "organizing" becomes "organising"."""
    uk = US_TO_UK[us]
    stem = us[:-1] if us.endswith("e") and uk.endswith("e") else us
    suffix = found[len(stem):]
    base = uk[:-1] if stem != us else uk
    out = base + suffix
    return out[0].upper() + out[1:] if found[0].isupper() else out


def us_spelling(text: str, line_no: int, **_) -> Iterator[Issue]:
    for m in US_PATTERN.finditer(text):
        us = US_KEYS[int(m.lastgroup[1:])]
        yield _issue("us-spelling", line_no, m, text,
                     f"US spelling \"{m.group(0)}\". UK English uses \"{_british_form(m.group(0), us)}\".")


AI_PHRASES = {
    "delve": "Say \"look at\" or \"explore\".",
    "tapestry": "Name the actual thing.",
    "in today's fast-paced": "Cut it. Every era thinks it's fast-paced.",
    "in today’s fast-paced": "Cut it. Every era thinks it's fast-paced.",
    "it's worth noting": "Just say the thing.",
    "it is worth noting": "Just say the thing.",
    "it's important to note": "Just say the thing.",
    "navigate the complexities": "Say what is hard and why.",
    "unlock the power": "Say what it actually does.",
    "unleash": "Say what it actually does.",
    "game-changer": "Show the change instead.",
    "game changer": "Show the change instead.",
    "seamless": "Few things are. Describe the experience.",
    "elevate your": "Say how it improves.",
    "a testament to": "Say what it proves.",
    "ever-evolving": "Cut it.",
    "ever-changing landscape": "Cut it.",
    "embark on a journey": "Say \"start\".",
    "let's dive in": "Just begin.",
    "in conclusion": "End on the point, not a signpost.",
    "furthermore": "Try \"and\" or \"also\".",
    "moreover": "Try \"and\" or \"also\".",
    "plethora": "Say \"many\".",
    "myriad": "Say \"many\".",
    "synergy": "Say how they work together.",
    "robust": "Say what makes it strong.",
    "cutting-edge": "Say what is new about it.",
    "harness the": "Say \"use\".",
}
AI_PATTERN = re.compile("|".join(rf"\b{re.escape(p)}" for p in sorted(AI_PHRASES, key=len, reverse=True)), re.IGNORECASE)
NOT_ONLY = re.compile(r"\bnot only\b[^.!?]*?\bbut\b", re.IGNORECASE)


def _quoted(text: str, m: re.Match) -> bool:
    """A phrase in quotation marks is being mentioned, not used."""
    before, after = text[max(0, m.start() - 1):m.start()], text[m.end():m.end() + 1]
    return before in "\"\u201c'\u2018" and before != "" and after in "\"\u201d'\u2019" and after != ""


def ai_phrases(text: str, line_no: int, **_) -> Iterator[Issue]:
    for m in NOT_ONLY.finditer(text):
        yield _issue("ai-phrases", line_no, m, text, "The \"not only X, but Y\" pattern reads as machine-made. Say both things plainly.")
    for m in AI_PATTERN.finditer(text):
        if _quoted(text, m):
            continue
        tip = AI_PHRASES.get(m.group(0).lower(), "")
        yield _issue("ai-phrases", line_no, m, text, f"\"{m.group(0)}\" sounds machine-made. {tip}".strip())


# ---------------------------------------------------------------- headings

SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into", "nor", "of", "on", "or", "the", "to", "via", "vs", "with"}


def title_case_headings(text: str, line_no: int, is_heading: bool = False, **_) -> Iterator[Issue]:
    if not is_heading:
        return
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
    lower = [w for w in words[1:] if w[0].islower() and w.lower() not in SMALL_WORDS]
    if lower:
        yield Issue("title-case-headings", line_no, 1, f"Heading isn't in Title Case: {', '.join(lower[:4])}.", text.strip()[:60])


RULES: dict[str, Rule] = {r.name: r for r in [
    Rule("em-dash", "No em dashes, double hyphens or spaced en dashes used as punctuation", em_dash),
    Rule("oxford-comma", "No serial comma before the final \"and\" or \"or\"", oxford_comma),
    Rule("stranded-preposition", "Sentences don't end on a preposition (phrasal verbs are fine)", stranded_preposition),
    Rule("us-spelling", "British spelling, with about 200 common US forms caught", us_spelling),
    Rule("ai-phrases", "No stock phrases that make writing sound machine-made", ai_phrases),
    Rule("exclamation", "No exclamation marks", exclamation),
    Rule("sentence-length", "Sentences of 30 words or fewer (configurable)", sentence_length),
    Rule("title-case-headings", "Markdown headings in Title Case", title_case_headings),
]}
