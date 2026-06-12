####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################
import logging
from exforparser.submodules.utilities.reaction import (
    sf6_to_mf,
    sf3_dict,
    sig_sf5,
    mt_fy_sf5,
)
from exfor_dictionary.exfor_dict import Diction

d = Diction("209")
chemical_compound_list = d.get_diction()


def filter_complex_reactions(entry_json, subent, pointer):
    # Check if operator exists (complex reactions)
    return entry_json["reactions"][subent][pointer]["operator"] is not None


def filter_reaction(react_dict, df):
    # Skip if arbitrary data is present or reaction type is invalid
    if not any(reac == react_dict["sf6"] for reac in sf6_to_mf):
        return True
    return df.empty or any(arb_unit == 1 for arb_unit in df["arbitrary_data"])


def filter_cross_section_case(react_dict, df):
    # Skip invalid cross-section cases
    if any(react_dict["target"] == cmp for cmp in chemical_compound_list.keys()):
        ## target is a compound (not nucleus)
        logging.info(f"{react_dict} skipped pattern 1")
        return True

    if not react_dict["process"].split(",")[0] in [
        "0",
        "N",
        "P",
        "D",
        "G",
        "T",
        "A",
        "HE3",
    ]:
        ## so far filtering charged particle reactions
        logging.info(f"{react_dict} skipped pattern 2")
        return True

    if not react_dict["process"].split(",")[1] in sf3_dict.keys():
        logging.info(f"{react_dict} skipped pattern 3")
        return True

    if react_dict["sf7"]:
        ## Skip the misc. data
        logging.info(f"{react_dict} skipped pattern 4")
        return True

    if any(
        excep in react_dict["sf8"]
        for excep in ["MSC", "REL", "FRC", "RES", "RAW"]
        if react_dict["sf8"]
    ):
        ## Skip the misc. data
        logging.info(f"{react_dict} skipped pattern 5")
        return True

    if df["en_inc"].isnull().values.all():
        logging.info(f"{react_dict} skipped pattern 6")
        return True

    return False


def filter_partial_cross_section_case(react_dict, df):
    if df["en_inc"].isnull().values.all():
        return True

    if (
        not react_dict.get("sf4")
        or react_dict["sf4"].endswith("-0")
        or react_dict["process"].split(",")[1] == "X"
    ):
        return True

    if (
        len(df["level_num"].unique())
        == 0
        # or not df["level_num"].unique().all()
    ):
        return True

    return False


def filter_angular_distribution_case(react_dict, df):
    if not react_dict["process"].split(",")[1] in sf3_dict.keys():
        return True

    if any(react_dict["sf8"] != excep for excep in ("EXP",) if react_dict["sf8"]):
        return True

    if react_dict["sf7"]:
        return True

    if react_dict["sf5"] is None or any(
        sf5 == react_dict["sf5"] for sf5 in sig_sf5.keys()
    ):
        if df["en_inc"].isnull().values.all():
            return True

    return False


def filter_partial_angular_distribution_case(react_dict, df):
    ## case for PAR,DA
    if df["en_inc"].isnull().values.all():
        return True

    if react_dict["sf4"].endswith("-0") or react_dict["process"].split(",")[1] == "X":
        return True

    if len(df["level_num"].unique()) == 0:
        return True

    return False


def filter_energy_distribution_case(react_dict, df):
    if (
        not any(par == react_dict["process"].split(",")[1] for par in sf3_dict.keys())
        or any(react_dict["sf8"] != excep for excep in ("EXP",) if react_dict["sf8"])
        or react_dict["sf7"]
    ):
        return True

    if df["en_inc"].isnull().values.all():
        return True

    if df["e_out"].isnull().values.all():
        return True

    if "arbitrary_data" in df.columns and df["arbitrary_data"].fillna(False).any():
        return True

    return False


def filter_double_differential_cross_section_case(react_dict, df):
    if filter_energy_distribution_case(react_dict, df):
        return True

    if df["angle"].isnull().values.all():
        return True

    if "y_unit" in df.columns:
        units = set(df["y_unit"].dropna().unique())
        if units and units != {"B/SR/EV"}:
            return True

    return False


def filter_neutron_observables_case(react_dict, df):
    if (
        any(
            excep in react_dict["sf8"]
            for excep in ["MSC", "REL", "FRC", "RES", "RAW"]
            if react_dict["sf8"]
        )
        or react_dict["sf7"]
    ):
        return True

    if df["en_inc"].isnull().values.all():
        return True

    return False


def filter_misc_neutron_observables_case(react_dict, df):
    if (
        any(
            excep in react_dict["sf8"]
            for excep in ["MSC", "REL", "FRC", "RES", "RAW", "NPD"]  # MXD is ok
            if react_dict["sf8"]
        )
        or react_dict["sf7"]
    ):
        return True

    if df["en_inc"].isnull().values.all():
        return True

    return False


def filter_kinetic_energy_case(react_dict, df):
    if (
        any(
            excep in react_dict["sf8"]
            for excep in ["MSC", "REL", "FRC", "RES", "RAW"]
            if react_dict["sf8"]
        )
        or react_dict["sf7"]
    ):
        return True

    if df["en_inc"].isnull().values.all():
        return True

    return False


def filter_fission_yield_case(react_dict, df):
    if (
        not any(par == react_dict["sf5"] for par in mt_fy_sf5.keys())
        or any(
            excep in react_dict["sf8"]
            for excep in ("MSC", "REL", "FRC", "RES", "RAW")
            if react_dict["sf8"]
        )
        or react_dict["sf7"]
    ):
        return True

    if df["en_inc"].isnull().values.all():
        return True

    return False
