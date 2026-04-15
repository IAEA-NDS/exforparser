"""Tests for json_converter helper functions."""
import pytest
from exforparser.json_converter import _fill_missing_references


def _make_entry_json(has_001_refs=False, subent_refs=None):
    """Build a minimal entry_json fixture."""
    refs = [{"x4_code": "(J,NST,50,1,(2013))", "free_txt": [], "doi": None, "publication_year": 2013}] if has_001_refs else []
    entry_json = {
        "bib_record": {"references": refs},
        "experimental_conditions": {
            "001": {"0": {}},
        },
    }
    if subent_refs:
        for subent, ref_list in subent_refs.items():
            entry_json["experimental_conditions"][subent] = {
                "0": {"reference": ref_list}
            }
    return entry_json


class TestFillMissingReferences:
    def test_no_op_when_001_has_references(self):
        entry_json = _make_entry_json(has_001_refs=True)
        original_refs = list(entry_json["bib_record"]["references"])
        _fill_missing_references(entry_json)
        assert entry_json["bib_record"]["references"] == original_refs

    def test_backfills_from_subentry(self):
        subent_refs = {
            "002": [{"x4_code": "(J,PR,100,1,(1955))", "free_txt": []}],
        }
        entry_json = _make_entry_json(subent_refs=subent_refs)
        _fill_missing_references(entry_json)
        assert len(entry_json["bib_record"]["references"]) == 1
        assert entry_json["bib_record"]["references"][0]["x4_code"] == "(J,PR,100,1,(1955))"

    def test_deduplicates_same_x4_code(self):
        subent_refs = {
            "002": [{"x4_code": "(J,PR,100,1,(1955))", "free_txt": []}],
            "003": [{"x4_code": "(J,PR,100,1,(1955))", "free_txt": []}],
        }
        entry_json = _make_entry_json(subent_refs=subent_refs)
        _fill_missing_references(entry_json)
        assert len(entry_json["bib_record"]["references"]) == 1

    def test_collects_multiple_unique_refs(self):
        subent_refs = {
            "002": [{"x4_code": "(J,PR,100,1,(1955))", "free_txt": []}],
            "003": [{"x4_code": "(J,NST,50,1,(2013))", "free_txt": []}],
        }
        entry_json = _make_entry_json(subent_refs=subent_refs)
        _fill_missing_references(entry_json)
        assert len(entry_json["bib_record"]["references"]) == 2

    def test_no_crash_when_no_subent_refs(self):
        entry_json = _make_entry_json()
        _fill_missing_references(entry_json)
        assert entry_json["bib_record"]["references"] == []
