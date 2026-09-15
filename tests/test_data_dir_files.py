"""Tests for tabulator output path helpers."""

import pytest

from exforparser.tabulator import data_dir_files
from exforparser.tabulator.data_dir_files import (
    exfortables_filename,
    get_dir_name,
    get_obs_dir_name,
    get_resonance_param_dir_name,
    get_thermal_filename,
    is_ion_projectile,
    level_num_reformat,
    nuclide_reformat,
    process_reformat,
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


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Fe56", "Fe-56"),
        ("Zr91", "Zr-91"),
        ("Ag110", "Ag-110"),
        ("Fe-56", "Fe-56"),
        ("Zr-91", "Zr-91"),
        ("Tc-99-M", "Tc-99-M"),
        ("Tc-99-N", "Tc-99-N"),
        ("43-TC-99-M", "Tc-99-M"),
        ("43-TC-99-N", "Tc-99-N"),
        ("0-NN-1", "0-NN-1"),
    ],
)
def test_nuclide_reformat_uses_one_hyphenated_representation(value, expected):
    assert nuclide_reformat(value) == expected


def test_exfortables_filename_formats_target_and_product_consistently():
    filename = exfortables_filename(
        "/tmp",
        "20690-005-0",
        "n-inl-L1",
        {"target": "26-FE-56"},
        {"first_author": "M.Hyakutake", "year": 1975},
        prod="Fe56",
    )

    assert filename.endswith(
        "Fe-56_n-inl-L1_Fe-56_M.Hyakutake-20690-005-0-1975.txt"
    )


@pytest.mark.parametrize(
    ("target", "process", "product", "author", "entry_id", "year", "expected"),
    [
        (
            "42-MO-100", "p-2n", "Tc-99-M", "K.Gagnon", "C2156-005-0", 2011,
            "Mo-100_p-2n_Tc-99-M_K.Gagnon-C2156-005-0-2011.txt",
        ),
        (
            "40-ZR-90", "n-g", "Zr91", "R.L.Macklin", "11845-002-0", 1963,
            "Zr-90_n-g_Zr-91_R.L.Macklin-11845-002-0-1963.txt",
        ),
        (
            "79-AU-197", "6-c-12-x", "Ag-110-1", "A.Yokoyama", "E2074-004-0", 2001,
            "Au-197_6-c-12-x_Ag-110-1_A.Yokoyama-E2074-004-0-2001.txt",
        ),
    ],
)
def test_representative_self_explanatory_filenames_are_preserved(
    target, process, product, author, entry_id, year, expected
):
    filename = exfortables_filename(
        "/tmp",
        entry_id,
        process,
        {"target": target},
        {"first_author": author, "year": year},
        prod=product,
    )

    assert filename.endswith(expected)


def test_level_num_reformat_uses_integer_notation():
    assert level_num_reformat(1) == "1"
    assert level_num_reformat(1.0) == "1"


def test_partial_reaction_dir_uses_integer_level_notation(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_dir_name(
        "exfortables_py",
        {"target": "26-FE-56", "process": "N,INL", "sf6": "DA"},
        level_num=1.0,
    )

    assert dirname == "/tmp/exfor/exfortables_py/n/Fe-56/n-inl-L1/angle/"


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


@pytest.mark.parametrize(
    ("projectile", "directory"),
    [
        ("0", "0"),
        ("A", "a"),
        ("D", "d"),
        ("E", "e"),
        ("G", "g"),
        ("H", "h"),
        ("HE3", "h"),
        ("N", "n"),
        ("P", "p"),
        ("T", "t"),
    ],
)
def test_particle_projectiles_use_top_level_directories(
    monkeypatch, projectile, directory
):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_dir_name(
        "exfortables_py",
        {"target": "1-H-1", "process": f"{projectile},EL", "sf6": "DA"},
    )

    assert dirname == (
        f"/tmp/exfor/exfortables_py/{directory}/H-1/"
        f"{directory}-el/angle/"
    )


def test_only_nuclide_projectiles_are_classified_as_heavy_ions():
    assert is_ion_projectile("4-BE-9")
    assert is_ion_projectile("2-HE-6")
    assert is_ion_projectile("2-HE-8")
    for projectile in ("A", "D", "HE3", "P", "T", "2-HE-4"):
        assert not is_ion_projectile(projectile)


@pytest.mark.parametrize("projectile", ["2-HE-6", "2-HE-8"])
def test_neutron_rich_helium_projectiles_use_ion_layout(monkeypatch, projectile):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_dir_name(
        "exfortables_py",
        {"target": "6-C-12", "process": f"{projectile},N", "sf6": "SIG"},
    )

    mass = projectile.split("-")[2]
    assert dirname == f"/tmp/exfor/exfortables_py/ion/C-12/He-{mass}/n/xs/"


def test_legacy_i_output_directory_is_never_returned():
    assert process_reformat({"process": "6-C-12,X"}) == "ion"
    assert process_reformat({"process": "PIP,EL"}) == "pip"


def test_scalar_filename_uses_the_shared_target_formatter():
    assert get_thermal_filename("/tmp", {"target": "26-FE-56"}) == (
        "/tmp/Fe-56.txt"
    )


def test_helium3_resonance_parameter_uses_h_directory(monkeypatch):
    monkeypatch.setattr(data_dir_files, "OUT_PATH", "/tmp/exfor")

    dirname = get_resonance_param_dir_name(
        "resonance_parameter",
        {
            "target": "3-LI-7",
            "process": "HE3,EL",
            "projectile": "HE3",
            "sf6": "SIG",
            "sf8": None,
        },
    )

    assert dirname == (
        "/tmp/exfor/exfortables_py/h/Li-7/h-el/"
        "resonance_parameter/SIG/"
    )


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
