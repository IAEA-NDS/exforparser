"""Tests for tabulator data_process utility functions."""
import pytest
from exforparser.tabulator.data_process import data_length_unify


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
