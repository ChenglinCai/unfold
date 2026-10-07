"""Word lists that the rules use."""

# Irregular past participles, for the passive-voice warning. Regular ones end in -ed.
# Some look like the present tense, such as "run" and "set". After a form of "be",
# they are past participles.
IRREGULAR_PARTICIPLES = frozenset(
    """
    arisen begun bent bound bitten blown broken brought built burnt bought caught
    chosen dealt done drawn driven eaten fallen fed felt fought found forgotten
    forgiven frozen given grown hung heard hidden held hurt kept known laid led left
    lent lost made meant met paid ridden risen said seen sought sold sent shaken
    shown shut sung sunk slept spoken spent split spread stood stolen stuck struck
    sworn swept taken taught torn told thought thrown understood woken worn won
    written run put set cut hit read
    """.split()
)

# Abbreviations, each with what a speaker would say instead.
ABBREVIATIONS = {
    "e.g.": "for example",
    "i.e.": "that is",
    "etc.": "and so on",
    "vs.": "versus",
    "cf.": "compare",
    "approx.": "about",
    "a.k.a.": "also known as",
    "w.r.t.": "with respect to",
    "et al.": "and others",
}
