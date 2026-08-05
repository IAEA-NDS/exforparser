"""Tests for tabulator data_process utility functions."""
import pytest
from exforparser.tabulator.data_process import (
    _frame_from_head,
    _observable_frame,
    data_length_unify,
)


def test_exfor_frame_defaults_and_explicit_qualifiers():
    assert _frame_from_head("ANG", default="LAB") == "LAB"
    assert _frame_from_head("E-CM", default="LAB") == "CM"
    assert _frame_from_head("DATA-LAB", default="LAB") == "LAB"
    assert _frame_from_head("DATA") is None


def test_ddx_observable_defaults_to_lab_frame():
    assert _observable_frame({"sf6": "DA/DE"}, None) == "LAB"
    assert _observable_frame({"sf6": "DA/DE"}, "CM") == "CM"
    assert _observable_frame({"sf6": "SIG"}, None) is None


class TestDataLengthUnify:
    def test_equal_length_unchanged(self):
        data = {
            "heads": ["EN", "DATA"],
            "units": ["MEV", "B"],
            "data": [[1.0, 2.0, 3.0], [0.1, 0.2, 0.3]],
        }
        result = data_length_unify(data)
        assert all(len(col) == 3 for col in result["data"])

    def test_short_column_padded(self):
        data = {
            "heads": ["EN-MEAN", "DATA"],
            "units": ["MEV", "B"],
            "data": [[5.0], [0.1, 0.2, 0.3]],
        }
        result = data_length_unify(data)
        assert result["data"][0] == [5.0, None, None]
        assert len(result["data"][0]) == 3

    def test_raises_on_unresolvable_mismatch(self):
        # After padding the max-length column cannot be shorter than itself
        # This verifies the ValueError guard works
        data = {
            "heads": ["A", "B", "C"],
            "units": ["1", "1", "1"],
            "data": [[1, 2, 3], [4, 5], [6]],
        }
        result = data_length_unify(data)
        assert all(len(col) == 3 for col in result["data"])

    def test_single_column(self):
        data = {
            "heads": ["DATA"],
            "units": ["B"],
            "data": [[1.0, 2.0]],
        }
        result = data_length_unify(data)
        assert result["data"] == [[1.0, 2.0]]
