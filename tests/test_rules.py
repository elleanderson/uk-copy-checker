import pytest

from ukcopy import check_text
from ukcopy.checker import Config


def rules(text, **kw):
    return [i.rule for i in check_text(text, config=Config(**kw))]


@pytest.mark.parametrize("text", ["Fast — and kind.", "Fast--and kind.", "Fast – and kind."])
def test_dashes_are_caught(text):
    assert "em-dash" in rules(text)


def test_hyphens_and_ranges_are_fine():
    assert "em-dash" not in rules("A well-made plan for 2025–2026.")


def test_oxford_comma():
    assert "oxford-comma" in rules("We looked at speed, cost, and quality.")
    assert "oxford-comma" not in rules("We looked at speed, cost and quality.")


@pytest.mark.parametrize("text", ["It was a project I'm proud of.", "Which team is it for?", "That's the tool I work with."])
def test_stranded_prepositions(text):
    assert "stranded-preposition" in rules(text)


@pytest.mark.parametrize("text", ["Let's get you set up.", "The change will kick in.", "Please sign in.", "It's something I look forward to."])
def test_phrasal_verbs_are_allowed(text):
    assert "stranded-preposition" not in rules(text)


@pytest.mark.parametrize("us,uk", [("organize", "organise"), ("colors", "colours"), ("analyzing", "analysing"),
                                    ("Behavior", "Behaviour"), ("centers", "centres"), ("catalog", "catalogue")])
def test_us_spelling_suggests_the_british_form(us, uk):
    issues = check_text(f"The {us} matters.")
    hit = [i for i in issues if i.rule == "us-spelling"]
    assert hit and f'"{uk}"' in hit[0].message


@pytest.mark.parametrize("word", ["size", "prize", "seize", "program", "practice", "meter"])
def test_words_that_are_correct_in_uk_english(word):
    assert "us-spelling" not in rules(f"The {word} matters.")


def test_ai_phrases():
    assert "ai-phrases" in rules("Let's delve into the tapestry of insight.")


def test_exclamation():
    assert "exclamation" in rules("We did it!")


def test_sentence_length_is_configurable():
    long = " ".join(["word"] * 35) + "."
    assert "sentence-length" in rules(long)
    assert "sentence-length" not in rules(long, max_sentence_words=40)


def test_headings_in_title_case():
    assert "title-case-headings" in rules("# how we prioritise work")
    assert "title-case-headings" not in rules("# How We Prioritise Work")
    assert "title-case-headings" not in rules("# A Guide to the Rules of Style")


def test_code_links_and_front_matter_are_ignored():
    md = "---\ntitle: color\n---\n\n```\ncolor = organize()\n```\n\nSee `color` at [the guide](https://example.com/color).\n"
    assert rules(md) == []


def test_disable_comments():
    md = "We prioritize it. <!-- ukcopy-disable-line -->\n<!-- ukcopy-disable -->\nColor.\n<!-- ukcopy-enable -->\nColor.\n"
    hits = [i.line for i in check_text(md) if i.rule == "us-spelling"]
    assert hits == [5]


def test_html_ignores_scripts_and_tags():
    page = '<p class="color">Our colour palette.</p><script>var color = 1;</script>'
    assert check_text(page, kind="html") == []


def test_disabled_rules():
    assert rules("We did it!", disabled={"exclamation"}) == []


def test_quoted_phrases_are_mentions_not_uses():
    assert "ai-phrases" not in rules('Avoid words such as "delve" in your copy.')


def test_comma_before_a_new_clause_is_fine():
    assert "oxford-comma" not in rules("I care about clear, warm writing, and I help teams build products.")


def test_inline_code_at_the_end_of_a_sentence():
    assert "stranded-preposition" not in rules("Install it with `pip install ukcopy`.")


def test_not_only_but_pattern():
    assert "ai-phrases" in rules("It's not only fast, but it's also kind.")
    assert "ai-phrases" not in rules("Useful for leaders, not only engineers.")
