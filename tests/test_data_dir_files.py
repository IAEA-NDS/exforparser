"""Tests for tabulator output path helpers."""

from exforparser.tabulator.data_dir_files import exfortables_filename


def test_exfortables_filename_preserves_author_initial():
    filename = exfortables_filename(
        "/tmp",
        "L0183-005",
        "",
        {"target": "56-BA-136", "process": "N,G"},
        {"first_author": "R.Massarczyk", "year": 2012},
    )

    assert filename.endswith("_R.Massarczyk-L0183-005-2012.txt")

