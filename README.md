<p align="center"><img src="https://andersonco.uk/leaf-oak.png" width="48" alt=""></p>

# UK Copy Checker

[![CI](https://github.com/elleanderson/uk-copy-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/elleanderson/uk-copy-checker/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%20to%203.13-12332E?logo=python&logoColor=F3EEE2)
![GitHub Action](https://img.shields.io/badge/GitHub%20Action-ready-12332E?logo=githubactions&logoColor=F3EEE2)
![Licence](https://img.shields.io/badge/licence-MIT-A8842F)

A house style checker for UK English. It reads your Markdown, text and HTML and points out the small things that make writing sound American, careless or machine-made, with a kinder suggestion for each one.

It runs in your terminal, in your editor's task runner or as a GitHub Action that leaves notes on pull requests.

## Why I Built It

Every team I've led has had a style guide, and every style guide has been ignored by the second sprint. Not because people don't care, but because nobody can hold forty rules in their head while writing to a deadline.

The rules that matter most to me are simple. Write in British English. Don't use em dashes. Leave out the Oxford comma. Never end a sentence on a preposition. Avoid the stock phrases that make writing sound as if a chatbot wrote it. This tool checks all of that automatically, so people can spend their attention on what they're actually saying.

I use it on my own website and on everything in this GitHub profile. This README passes its own checks, and the build fails if it ever stops.

## What It Checks

| Rule | What It Looks For |
|---|---|
| `em-dash` | Em dashes, double hyphens and spaced en dashes used as punctuation |
| `oxford-comma` | A comma before the final "and" or "or" in a list |
| `stranded-preposition` | Sentences that end on "of", "for", "with" and similar words, while allowing phrasal verbs such as "set up" and "sign in" |
| `us-spelling` | About 200 common US spellings, with the matching British form for each, including plurals and "-ing" forms |
| `ai-phrases` | Stock phrases such as "delve", "tapestry" and "unlock the power", each with a plainer alternative |
| `exclamation` | Exclamation marks |
| `sentence-length` | Sentences over 30 words, which you can change |
| `title-case-headings` | Markdown headings that aren't in Title Case |

It skips code blocks, inline code, links, front matter, HTML tags, scripts and styles, so it only judges the words people will read. It also leaves alone the words that are correct in both countries, such as "program" for software and "meter" for a gas meter.

## Before and After

```text
$ ukcopy check examples/before.md

examples/before.md:3:24  ai-phrases            "delve" sounds machine-made. Say "look at" or "explore".
examples/before.md:3:74  em-dash               Avoid dashes as punctuation. Use a full stop, comma, colon or brackets.
examples/before.md:5:25  oxford-comma          Drop the comma before the final "and" or "or".
examples/before.md:5:39  stranded-preposition  Sentence ends on "of". Rewrite so it ends on a stronger word.
examples/before.md:7:67  us-spelling           US spelling "colors". UK English uses "colours".

12 issues in 1 file: 4 ai-phrases, 3 us-spelling, 1 title-case-headings, 1 em-dash, 1 exclamation, 1 oxford-comma, 1 stranded-preposition
```

The rewritten [`examples/after.md`](examples/after.md) passes cleanly.

## Getting Started

You'll need Python 3.10 or later.

```bash
pip install git+https://github.com/elleanderson/uk-copy-checker.git

ukcopy check README.md docs/          # check files or whole folders
ukcopy check site/ --format json      # machine-readable output
ukcopy check --stdin < draft.md       # check a draft from another tool
ukcopy rules                          # list every rule
```

The command exits with `1` when it finds something to fix, which makes it easy to use in scripts and pre-commit hooks. Add `--no-fail` to report without failing.

## Use It as a GitHub Action

Add this to a workflow and every pull request gets inline notes on the lines that need attention.

```yaml
- uses: actions/checkout@v4
- uses: elleanderson/uk-copy-checker@v1.0.0
  with:
    paths: docs/ README.md
    disable: sentence-length
    fail-on-issues: true
```

## Make It Yours

Put a `.ukcopy.toml` file in your project, or a `[tool.ukcopy]` section in `pyproject.toml`.

```toml
disable = ["sentence-length"]
max-sentence-words = 28
allow = ["Center for Executive Coaching"]   # proper nouns that keep their US spelling
```

To skip a line, add `<!-- ukcopy-disable-line -->` to it. To skip a block, wrap it in `<!-- ukcopy-disable -->` and `<!-- ukcopy-enable -->`.

## Using It from Python

```python
from ukcopy import check_text

for issue in check_text("We prioritized speed, cost, and quality."):
    print(issue.rule, issue.message)
```

## How It's Built

- **Python 3.10 to 3.13**, with no dependencies beyond the standard library on modern Python
- **A rule registry**, where each rule is a small, readable function that's easy to test and easy to switch off
- **pytest**, with tests for every rule, the edge cases and the command-line tool
- **GitHub Actions**, testing four Python versions on every push and checking this repository's own writing with the Action itself
- **A composite GitHub Action** that installs the package and turns results into pull request annotations

## Contributing

Ideas for new rules and better British spellings are very welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## About Me

I'm [Elle Anderson](https://andersonco.uk), a product leader and executive coach (Fellow, Chartered Institute for IT). I care about clear, warm writing, and I help teams build products and content that people trust. You might also enjoy my [AI Glossary for Product Leaders](https://andersonco.uk/ai-glossary).

## Licence

MIT. Use it, adapt it and build on it.
