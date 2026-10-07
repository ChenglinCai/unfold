"""The profile decides what may be public, and flags weak sources."""

import pytest

from unfold.sources.profile import needs, public_outputs, quality


@pytest.mark.parametrize(
    "license_name",
    ["CC BY 4.0", "CC-BY-SA-3.0", "cc by-sa 4.0", "CC0", "Public domain"],
)
def test_open_licenses_allow_public_outputs(license_name: str) -> None:
    assert public_outputs(license_name)


@pytest.mark.parametrize(
    "license_name",
    ["CC BY-NC 4.0", "CC BY-NC-SA 4.0", "CC BY-ND 4.0", "private", "unknown", "", None],
)
def test_other_licenses_keep_outputs_private(license_name: str | None) -> None:
    assert not public_outputs(license_name)


def test_flags_pages_with_almost_no_text() -> None:
    assert quality(words=20, units=4, unit="page")["low"] is True
    assert quality(words=1600, units=4, unit="page")["low"] is False
    assert quality(words=1600, units=4, unit="page")["words_per_page"] == 400


def test_each_family_has_a_main_need() -> None:
    assert needs("slides") == "fill-gaps"
    assert needs("textbook") == "cut"
    assert needs("topic") == "fact-check"
