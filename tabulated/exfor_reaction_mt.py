import sys
import json

sys.path.append("../")
from utilities.operation_util import slices


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

    return mt_dict, sf3_dict



def e_lvl_to_mt50(level_num):
    mt = list(range(50,91))
    if level_num is None:
        return "99"
    elif int(level_num) < 40:
        return str(mt[int(level_num)])
    else:
        return "91"