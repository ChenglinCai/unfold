"""The understand step: a knowledge map and study notes from one source.

One model job reads the source document and replies with both outputs. Code
checks them, retries with the errors as feedback, and saves the result under a
key. The key hashes the prompt, the request, and the model, so a second run on
unchanged inputs makes no model call.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from unfold import jobs
from unfold.sources import SourceDocument, load
from unfold.understand.checks import check_map, check_notes

PROMPT = Path(__file__).with_name("prompt.md")
OUTPUTS = "understand"
MAP_FILE = "knowledge-map.yaml"
NOTES_FILE = "study-notes.md"
RECORD_FILE = "job.json"
DEFAULT_MODEL = "sonnet"
RETRIES = 3
# One call reads the whole source. Prose ran about 1.8 tokens a word in a measured
# run, and text full of TeX may run near 2.5, so 60,000 words stay under about
# 150,000 tokens. That leaves room for the prompt and the reply in a 200,000-token
# context.
MAX_WORDS = 60_000
FENCE = re.compile(r"^```[a-z]*\n(.*?)\n?```$", re.DOTALL)


@dataclass(frozen=True)
class Result:
    folder: Path
    record: jobs.Record
    reused: bool


def request(doc: SourceDocument) -> str:
    """The job's input: the source's facts, then its text."""
    needs = doc.profile.get("needs", "")
    if doc.family == "topic":
        return (
            f"Source id: {doc.id}\nTopic: {doc.title}\nNeeds: {needs}\n\n"
            "This is a bare topic, with no source text."
        )
    listing = "\n".join(f"- {anchor.id}: {anchor.title}" for anchor in doc.anchors)
    return (
        f"Source id: {doc.id}\nTitle: {doc.title}\nFamily: {doc.family}\n"
        f"Needs: {needs}\nAnchors:\n{listing}\n\n<source>\n{doc.text()}</source>"
    )


def understand(
    source: Path,
    *,
    runner: jobs.Runner,
    model: str = DEFAULT_MODEL,
    retries: int = RETRIES,
) -> Result:
    """Write the outputs into source/understand, or reuse a saved result."""
    doc = load(source)
    system = PROMPT.read_text(encoding="utf-8")
    prompt = request(doc)
    out = source / OUTPUTS
    saved = jobs.Record.load(out / RECORD_FILE)
    key = jobs.key(system, prompt, model)
    if saved and saved.key == key and saved.outcome == "ok" and _passes(out, doc):
        return Result(out, saved, reused=True)
    record = jobs.Record(key=key, model=model)
    words = sum(len(anchor.text.split()) for anchor in doc.anchors)
    if words > MAX_WORDS:
        record.errors = [
            f"the source holds {words:,} words, and one call reads at most "
            f"{MAX_WORDS:,}. Ingest one chapter or part of it instead"
        ]
        return _give_up(out, record)
    ask = prompt
    for _ in range(retries + 1):
        try:
            reply = runner(ask, system=system, model=model)
        except jobs.JobError as error:
            record.errors = [str(error)]
            break
        record.add(reply)
        knowledge_map, notes, record.errors = read_reply(reply.text, doc, model)
        if not record.errors:
            record.outcome = "ok"
            out.mkdir(exist_ok=True)
            _write(out / MAP_FILE, knowledge_map)
            _write(out / NOTES_FILE, notes)
            record.save(out / RECORD_FILE)
            return Result(out, record, reused=False)
        record.tries.append(list(record.errors))
        ask = _retry(prompt, reply.text, record.errors)
    return _give_up(out, record)


def _give_up(out: Path, record: jobs.Record) -> Result:
    """Save a failed record, and leave any older outputs in place."""
    record.outcome = "failed"
    out.mkdir(exist_ok=True)
    record.save(out / RECORD_FILE)
    return Result(out, record, reused=False)


def read_reply(
    text: str, doc: SourceDocument, model: str
) -> tuple[str, str, list[str]]:
    """Split a reply into its two outputs, tidy the map, and check both."""
    parts = {name: _part(text, name) for name in ("knowledge-map", "study-notes")}
    missing = [
        f"the reply has no <{name}> part"
        for name, part in parts.items()
        if part is None
    ]
    if missing:
        return "", "", missing
    knowledge_map = _tidy(parts["knowledge-map"] or "", doc, model)
    notes = (parts["study-notes"] or "").strip() + "\n"
    return knowledge_map, notes, check_map(knowledge_map, doc) + check_notes(notes, doc)


def _part(text: str, name: str) -> str | None:
    match = re.search(rf"<{name}>\s*\n?(.*?)\s*</{name}>", text, re.DOTALL)
    if match is None:
        return None
    body = match.group(1).strip()
    fenced = FENCE.match(body)
    return fenced.group(1) if fenced else body


def _tidy(text: str, doc: SourceDocument, model: str) -> str:
    """Fill in what code knows: provenance, empty lists, and the flags of a bare topic."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return text
    if not isinstance(data, dict):
        return text
    head = {name: data.pop(name) for name in ("format", "source") if name in data}
    data = {**head, "written_by": f"unfold understand, model {model}", **data}
    for concept in data.get("concepts") or []:
        if isinstance(concept, dict):
            concept.setdefault("requires", [])
            concept.setdefault("anchors", [])
    if doc.family == "topic":
        for claim in data.get("claims") or []:
            if isinstance(claim, dict):
                claim["unsupported"] = True
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def _retry(prompt: str, answer: str, errors: list[str]) -> str:
    problems = "\n".join(f"- {error}" for error in errors)
    return (
        f"{prompt}\n\n<last-answer>\n{answer}\n</last-answer>\n\n"
        f"Your last answer failed these checks:\n{problems}\n\n"
        "Write the whole answer again, with every problem fixed."
    )


def _passes(out: Path, doc: SourceDocument) -> bool:
    paths = out / MAP_FILE, out / NOTES_FILE
    if not all(path.is_file() for path in paths):
        return False
    knowledge_map, notes = (path.read_text(encoding="utf-8") for path in paths)
    return not check_map(knowledge_map, doc) and not check_notes(notes, doc)


def _write(path: Path, text: str) -> None:
    partial = path.with_name(f".{path.name}.partial")
    partial.write_text(text, encoding="utf-8")
    partial.replace(path)
