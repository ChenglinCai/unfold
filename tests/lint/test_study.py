"""The breath-group study, run on a tiny invented corpus.

Real transcripts have no license, so tests never use them.
"""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

STUDY = Path(__file__).resolve().parents[2] / "corpus" / "breath_groups.py"
TEXT = "One two three, four five. Six seven eight nine ten eleven twelve thirteen.\n"
WORDS = TEXT.split()


@pytest.fixture
def study() -> ModuleType:
    spec = importlib.util.spec_from_file_location("breath_groups", STUDY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def timings() -> list[list[object]]:
    """Each word lasts 0.3 seconds. A 0.3-second pause follows "three," and 0.5 "five."."""
    out, clock = [], 0.0
    for word in WORDS:
        out.append([" " + word, round(clock, 2), round(clock + 0.3, 2)])
        clock += 0.3 + {"three,": 0.3, "five.": 0.5}.get(word, 0.0)
    return out


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    for video in ("2019/video-a", "2020/video-b"):
        folder = tmp_path / video / "english"
        folder.mkdir(parents=True)
        (folder / "transcript.txt").write_text(TEXT, encoding="utf-8")
        (folder / "word_timings.json").write_text(
            json.dumps(timings()), encoding="utf-8"
        )
    return tmp_path


def test_finds_every_english_transcript(study: ModuleType, corpus: Path) -> None:
    assert [t.name for t in study.load(corpus)] == ["2019/video-a", "2020/video-b"]


def test_measures_breath_groups(study: ModuleType) -> None:
    assert study.group_lengths(TEXT) == [3, 2, 8]


def test_takes_nearest_rank_percentiles(study: ModuleType) -> None:
    assert study.percentile([1, 2, 3, 4, 10], 0.9) == 10
    assert study.percentile([1, 2, 3, 4, 10], 0.5) == 3


def test_compares_punctuation_with_real_pauses(study: ModuleType) -> None:
    rows = [(str(w), float(s), float(e)) for w, s, e in timings()]  # type: ignore[arg-type]
    assert study.pause_agreement(rows, 0.25) == (1.0, 1.0)
    assert study.pause_agreement(rows, 0.4) == (0.5, 1.0)


def test_measures_speaking_rate(study: ModuleType) -> None:
    rows = [(str(w), float(s), float(e)) for w, s, e in timings()]  # type: ignore[arg-type]
    seconds = rows[-1][2] - rows[0][1]
    assert study.speaking_rate(rows) == pytest.approx(len(WORDS) / seconds * 60)


def test_calibrates_the_smallest_rare_limit(study: ModuleType) -> None:
    assert study.calibrate([3, 2, 8], total_words=13, per_thousand=1.0) == 8


def test_sets_aside_transcripts_without_punctuation(study: ModuleType) -> None:
    punctuated = study.Transcript("a", TEXT, [])
    bare = study.Transcript("b", "one two three four five six seven eight nine", [])
    empty = study.Transcript("c", "", [])
    keep, set_aside, cutoff = study.usable([punctuated, punctuated, bare, empty])
    assert [t.name for t in keep] == ["a", "a"]
    assert [t.name for t in set_aside] == ["b", "c"]
    assert cutoff > 0


def test_the_report_holds_numbers_and_no_transcript_text(
    study: ModuleType, corpus: Path, tmp_path: Path
) -> None:
    out = tmp_path / "report.md"
    study.main([str(corpus), "--out", str(out)])
    report = out.read_text(encoding="utf-8")
    assert "Transcripts: 2" in report
    assert "thirteen" not in report.lower()
