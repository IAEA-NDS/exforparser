"""Tests for tabulator data_process utility functions."""
import pandas as pd
import pytest
from exforparser.tabulator import data_process
from exforparser.tabulator.data_process import (
    _frame_from_head,
    _isomer_state_reformat,
    _observable_frame,
    data_length_unify,
    get_residual,
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


@pytest.mark.parametrize(
    ("processor", "writer_name"),
    [
        (
            data_process.process_partial_cross_section_case,
            "write_to_exfortables_format_sig",
        ),
        (
            data_process.process_partial_angular_distribution_case,
            "write_to_exfortables_format_da",
        ),
    ],
)
def test_partial_observable_filename_uses_integer_level_notation(
    monkeypatch, processor, writer_name
):
    processes = []
    products = []

    def capture_filename(directory, entry_id, process, react_dict, bib, en, prod):
        processes.append(process)
        products.append(prod)
        return "/tmp/output.txt"

    monkeypatch.setattr(data_process, "get_dir_name", lambda *args, **kwargs: "/tmp")
    monkeypatch.setattr(data_process, "exfortables_filename", capture_filename)
    monkeypatch.setattr(data_process, writer_name, lambda *args, **kwargs: None)

    df = pd.DataFrame(
        {"level_num": [1.0], "residual": ["Fe56"], "mf": [4], "mt": [51]}
    )
    react_dict = {"target": "26-FE-56", "process": "N,INL", "sf6": "DA"}

    processor(df, "40088-005-0", {}, react_dict)

    assert processes == ["n-inl-L1"]
    assert products == ["Fe-56"]


def test_numeric_isomer_state_uses_integer_notation_in_residual():
    data_dict = {
        "heads": ["DATA", "ELEMENT", "MASS", "ISOMER"],
        "units": ["B", "NO-DIM", "NO-DIM", "NO-DIM"],
        "data": [[1.0], [54.0], [125.0], [0.0]],
    }

    _, _, _, state, residual, _ = get_residual(
        {"locs_y": [0]},
        {"sf4": "ELEM/MASS"},
        data_dict,
    )

    assert state == ["0"]
    assert residual == ["Xe-125-0"]
    filename = data_process.exfortables_filename(
        "/tmp",
        "E2074-004-0",
        "6-c-12-x",
        {"target": "79-AU-197"},
        {"first_author": "A.Yokoyama", "year": 2001},
        prod=residual[0],
    )
    assert filename.endswith(
        "Au-197_6-c-12-x_Xe-125-0_A.Yokoyama-E2074-004-0-2001.txt"
    )


def test_non_integer_isomer_state_is_rejected():
    with pytest.raises(ValueError, match="must be an integer"):
        _isomer_state_reformat(1.5)


def test_symbolic_isomer_state_is_preserved():
    assert _isomer_state_reformat("M") == "M"


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
