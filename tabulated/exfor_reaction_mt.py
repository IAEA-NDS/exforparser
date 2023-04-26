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
import sys
import json

sys.path.append("../")
from utilities.utilities import slices


mt_fy = {
    "CUM": "459",
    "CHN": "459",
    "IND": "454",
    "SEC": "454",
    "MAS": "454",
    "SEC/CHN": "454",
    "CHG": "454",
    "PRE": "460",
    "PRV": "460",
    "TER": "460",
    "QTR": "460",
    "PR": "460",
}

rp_sig = {"IND": "RP", "CUM": "RP", "(CUM)": "RP", "M+": "RP", "M-": "RP", "(M)": "RP"}

mt_sig = {
    "CUM": "459",
    "CHN": "459",
    "IND": "454",
    "SEC": "454",
    "MAS": "454",
    "SEC/CHN": "454",
    "CHG": "454",
    "PRE": "460",
    "PRV": "460",
    "TER": "460",
    "QTR": "460",
    "PR": "460",
}

mt_nu_sf5 = {
    "": "452",
    "PR": "456",
    "SEC/PR": "Miscellaneous",
    "DL": "455",
    "TER": "456",
    "DL/CUM": "455",
    "DL/GRP": "DNgroup",
    "PR/TER": "Miscellaneous",
    "PRE/PR/FRG": "Miscellaneous",
    "PR/FRG": "Miscellaneous",
    "PR/PAR": "Miscellaneous",
    "PR/NUM": "Miscellaneous",
    "NUM": "Miscellaneous",
}

mt_spec = {
    "": "452",
    "PR": "456",
    "DL": "455",
    "DL/CUM": "455",
    "DL/GRP": "DNgroup",
    "PR/TER": "Miscellaneous",
    "PR/FRG": "Miscellaneous",
    "PR/NUM": "Miscellaneous",
    "NUM": "Miscellaneous",
}


def mt_to_reaction():
    with open("tabulated/MTall.dat") as f:
        lines = f.readlines()

    mt_dict = {}
    sf3_dict = {}
    for line in lines:
        if line.startswith("#"):
            continue

        data = line.strip().split()

        mt_dict[data[0]] = {}
        mt_dict[data[0]]["reaction"] = data[1] if len(data) >= 2 else None
        mt_dict[data[0]]["sf3"] = data[2] if len(data) >= 3 else None
        mt_dict[data[0]]["sf5-8"] = data[3] if len(data) >= 4 else None

        sf3_dict[data[2]] = {}  # if len(data) >= 3 else None: {} }
        sf3_dict[data[2]]["mt"] = data[0]
        sf3_dict[data[2]]["reaction"] = data[1] if len(data) >= 2 else None
        sf3_dict[data[2]]["sf5-8"] = data[3] if len(data) >= 4 else None

    return sf3_dict


sf3_dict = mt_to_reaction()


def e_lvl_to_mt50(level_num):
    mt = list(range(50, 91))
    if level_num is None:
        return "99"
    elif int(level_num) < 40:
        return str(mt[int(level_num)])
    else:
        return "91"


sf_to_mf = {
    "NU": "1",
    "WID": "2",
    "ARE": "2",
    "D": "2",
    "EN": "2",
    "J": "2",
    "SIG": "3",
    "DA": "4",
    "DE": "5",
    "FY": "8",
    "DA/DE": "6",
}


def get_mf(react_dict):

    if sf_to_mf.get(react_dict["sf6"]):
        if react_dict["sf6"] == "NU":
            return sf_to_mf[react_dict["sf6"]]

        elif react_dict["sf4"] == "0-G-0":
            return "12"  # Multiplicity of photon production

        else:
            return sf_to_mf[react_dict["sf6"]]
    else:
        return "?"


def get_mt(react_dict):

    if (
        react_dict["process"].split(",")[0] == "N"
        and react_dict["process"].split(",")[1] == "INL"
    ):
        return "4"

    elif (
        react_dict["process"].split(",")[0] != "N"
        and react_dict["process"].split(",")[1] == "N"
    ):
        return "4"

    else:
        return sf3_dict[react_dict["process"].split(",")[1]]["mt"]
