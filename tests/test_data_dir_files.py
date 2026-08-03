"""Tests for tabulator output path helpers."""

from exforparser.tabulator import data_dir_files
from exforparser.tabulator.data_dir_files import exfortables_filename, get_dir_name


def test_exfortables_filename_preserves_author_initial():
    filename = exfortables_filename(
        "/tmp",
        "L0183-005",
        "",
        {"target": "56-BA-136", "process": "N,G"},
        {"first_author": "R.Massarczyk", "year": 2012},
    )

    assert filename.endswith("_R.Massarczyk-L0183-005-2012.txt")


def test_ion_cross_section_dir_uses_target_projectile_outgoing_layout(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_dir_name(
        "exfortables_py",
        {"target": "90-TH-232", "process": "4-BE-9,F", "sf6": "SIG"},
    )

    assert dirname == "/tmp/exfor/exfortables_py/ion/Th-232/Be-9/f/xs/"


def test_ion_observable_dir_formats_nuclides_and_uses_outgoing_particle(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_dir_name(
        "exfortables_py",
        {"target": "2-HE-4", "process": "4-BE-7,P", "sf6": "DA"},
    )

    assert dirname == "/tmp/exfor/exfortables_py/ion/He-4/Be-7/p/angle/"
