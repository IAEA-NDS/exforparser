"""Tests for tabulator output path helpers."""

from exforparser.tabulator import data_dir_files
from exforparser.tabulator.data_dir_files import (
    exfortables_filename,
    get_dir_name,
    get_obs_dir_name,
    get_resonance_param_dir_name,
)


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


def test_legacy_i_projectile_uses_unified_ion_layout(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_dir_name(
        "exfortables_py",
        {"target": "1-H-1", "process": "PIP,EL", "sf6": "DA"},
    )

    assert dirname == "/tmp/exfor/exfortables_py/ion/H-1/PIP/el/angle/"


def test_ion_named_observable_uses_unified_ion_layout(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_obs_dir_name(
        "thermal",
        {"target": "90-TH-232", "process": "4-BE-9,F"},
    )

    assert dirname == "/tmp/exfor/exfortables_py/ion/Th-232/Be-9/f/thermal"


def test_ion_resonance_parameter_uses_unified_ion_layout(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_resonance_param_dir_name(
        "resonance_parameter",
        {
            "target": "90-TH-232",
            "process": "4-BE-9,F",
            "projectile": "4-BE-9",
            "sf6": "SIG",
            "sf8": None,
        },
    )

    assert dirname == (
        "/tmp/exfor/exfortables_py/ion/Th-232/Be-9/f/"
        "resonance_parameter/SIG/"
    )
