import pandas as pd
import pytest
from exforparser.tabulator.data_filter import (
    filter_reaction,
    filter_cross_section_case,
)


def _make_df(en_inc=None, arbitrary_data=None):
    """Helper: build a minimal DataFrame like process_general() returns."""
    return pd.DataFrame({
        "en_inc": en_inc if en_inc is not None else [1e6, 2e6],
        "arbitrary_data": arbitrary_data if arbitrary_data is not None else [False, False],
    })


def test_filter_reaction_skips_unknown_sf6():
    react_dict = {"sf6": "UNKNOWN_QUANTITY"}
    df = _make_df()
    assert filter_reaction(react_dict, df) is True   # should be skipped


def test_filter_reaction_skips_arbitrary_data():
    react_dict = {"sf6": "SIG"}
    df = _make_df(arbitrary_data=[1, 1])             # ARB-UNIT flag
    assert filter_reaction(react_dict, df) is True


def test_filter_reaction_passes_normal_case():
    react_dict = {"sf6": "SIG"}
    df = _make_df()
    assert filter_reaction(react_dict, df) is False  # should NOT be skipped


def test_filter_cross_section_skips_null_energy():
    react_dict = {
        "target": "92-U-238",
        "process": "N,F",
        "sf5": None,
        "sf7": None,
        "sf8": None,
    }
    df = _make_df(en_inc=[None, None])
    assert filter_cross_section_case(react_dict, df) is True


@pytest.mark.parametrize(
    "projectile", ["0", "A", "D", "E", "G", "H", "HE3", "N", "P", "T"]
)
def test_filter_cross_section_accepts_particle_projectiles(projectile):
    react_dict = {
        "target": "13-AL-27",
        "process": f"{projectile},EL",
        "sf5": None,
        "sf7": None,
        "sf8": None,
    }

    assert filter_cross_section_case(react_dict, _make_df()) is False


@pytest.mark.parametrize("projectile", ["2-HE-6", "2-HE-8"])
def test_filter_cross_section_accepts_neutron_rich_helium_ions(projectile):
    react_dict = {
        "target": "6-C-12",
        "process": f"{projectile},N",
        "sf5": None,
        "sf7": None,
        "sf8": None,
    }

    assert filter_cross_section_case(react_dict, _make_df()) is False
