"""American to British spelling pairs.

Kept as explicit word lists rather than blanket suffix rules, because English
is full of exceptions. "Size", "prize" and "capsize" keep their z. "Program" is
right for software, "meter" is right for a gas meter, "judgment" is right in a
court and "practice" is the noun in both. Each entry covers the base form; the
checker also catches common inflections (s, d, ed, ing, r, rs).
"""

IZE_TO_ISE = [
    "apologize", "authorize", "capitalize", "categorize", "characterize", "civilize", "criticize",
    "customize", "digitize", "emphasize", "finalize", "formalize", "generalize", "harmonize",
    "humanize", "idealize", "industrialize", "itemize", "legalize", "localize", "maximize",
    "memorize", "minimize", "mobilize", "modernize", "monetize", "normalize", "optimize",
    "organize", "personalize", "prioritize", "publicize", "randomize", "realize", "recognize",
    "socialize", "specialize", "standardize", "stabilize", "summarize", "sympathize",
    "synchronize", "utilize", "visualize", "operationalize", "productize", "incentivize",
    "democratize", "energize", "jeopardize", "mesmerize", "neutralize", "patronize",
    "scrutinize", "strategize", "subsidize", "symbolize", "tokenize", "vaporize", "verbalize",
]
IZATION_TO_ISATION = [w[:-1] + "ation" for w in IZE_TO_ISE if not w.endswith("tize")] + [
    "digitization", "monetization", "democratization", "tokenization", "prioritization",
]
YZE_TO_YSE = ["analyze", "paralyze", "catalyze"]
OR_TO_OUR = [
    "behavior", "color", "favor", "favorite", "flavor", "harbor", "honor", "humor", "labor",
    "neighbor", "rumor", "savior", "valor", "vapor", "endeavor", "glamor", "parlor", "rigor",
    "candor", "clamor", "fervor", "odor", "splendor", "tumor", "armor",
]
ER_TO_RE = ["center", "fiber", "liter", "theater", "somber", "caliber", "saber", "luster"]
MISC = {
    "aluminum": "aluminium", "catalog": "catalogue", "dialog": "dialogue", "analog": "analogue",
    "defense": "defence", "offense": "offence", "pretense": "pretence",
    "enroll": "enrol", "fulfill": "fulfil", "skillful": "skilful", "willful": "wilful",
    "gray": "grey", "jewelry": "jewellery", "mold": "mould", "plow": "plough", "pajamas": "pyjamas",
    "skeptical": "sceptical", "skeptic": "sceptic", "traveled": "travelled",
    "traveling": "travelling", "traveler": "traveller", "canceled": "cancelled",
    "canceling": "cancelling", "modeling": "modelling", "modeled": "modelled",
    "labeled": "labelled", "labeling": "labelling", "fueled": "fuelled", "leveled": "levelled",
    "counselor": "counsellor", "acknowledgment": "acknowledgement",
    "mom": "mum", "cozy": "cosy", "donut": "doughnut", "maneuver": "manoeuvre",
    "pediatric": "paediatric", "anesthetic": "anaesthetic", "encyclopedia": "encyclopaedia",
    "esthetic": "aesthetic", "estrogen": "oestrogen", "fetus": "foetus",
    "license plate": "number plate", "airplane": "aeroplane",
}


def _pairs() -> dict[str, str]:
    pairs: dict[str, str] = {}
    for w in IZE_TO_ISE:
        pairs[w] = w[:-3] + "ise"
    for w in IZATION_TO_ISATION:
        pairs[w] = w.replace("ization", "isation")
    for w in YZE_TO_YSE:
        pairs[w] = w[:-3] + "yse"
    for w in OR_TO_OUR:
        pairs[w] = w[:-2] + "our"
    for w in ER_TO_RE:
        pairs[w] = w[:-2] + "re"
    pairs.update(MISC)
    return pairs


US_TO_UK: dict[str, str] = _pairs()
