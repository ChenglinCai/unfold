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

# Words and phrases that mark AI writing, from Wikipedia's "Signs of AI writing":
# https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
# Common words with ordinary uses, such as "key" and "highlight", stay out, because
# a video tool highlights things and a cache has keys.
AI_VOCABULARY = frozenset(
    """
    additionally boast boasts boasted bolster bolsters bolstered bolstering crucial
    delve delves delved delving emphasizing enduring enhance enhances enhanced
    enhancing foster fosters fostered fostering garner garners garnered garnering
    groundbreaking interplay intricate meticulous meticulously nestled pivotal
    renowned showcase showcases showcased showcasing tapestry testament underscore
    underscores underscored underscoring valuable vibrant
    """.split()
)
AI_PHRASES = (
    r"\bnot only\b.{0,80}?\bbut also\b",
    r"\bit(?:'s|\u2019s| is) not just\b",
    r"\bit(?:'s|\u2019s| is) important to (?:note|remember)\b",
    r"\b(?:serves|served|stands|stood|functions) as\b",
    r"\bplays? an? (?:crucial|pivotal|key|vital|significant) role\b",
    r"\bin (?:summary|conclusion)\b",
    r"\b(?:ever-)?evolving landscape\b",
    r"\baligns? with\b",
)
