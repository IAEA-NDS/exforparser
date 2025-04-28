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
# import os
# import json
# from ..config import MT_DEF, MF3_JSON

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


sf6_to_dir = {
    "SIG": "xs",
    "DA": "angle",
    "DE": "energy",
    "NU": "neutrons",
    "DL": "neutrons",
    "NU/DE": "neutrons/energy",
    "FY": "fission/yield",
    "FY/DE": "fission/energy",
    "KE": "kinetic_energy",
    "AKE": "kinetic_energy/average",
}


## The allowed SF5 for SIG data
sig_sf5 = {"IND": "RP", "CUM": "RP", "(CUM)": "RP", "M+": "RP", "M-": "RP", "(M)": "RP"}


## The MT number allocation and directory name for FY data
mt_fy_sf5 = {
    "CUM": {"mt": "459", "name": "cumulative"},
    "CHN": {"mt": "459", "name": "cumulative"},
    "IND": {"mt": "454", "name": "independent"},
    "SEC": {"mt": "454", "name": "independent"},
    "MAS": {"mt": "454", "name": "independent"},
    "SEC/CHN": {"mt": "454", "name": "independent"},
    "CHG": {"mt": "454", "name": "independent"},
    "PRE": {"mt": "460", "name": "primary"},
    "PRV": {"mt": "460", "name": "primary"},
    "TER": {"mt": "460", "name": "primary"},
    "QTR": {"mt": "460", "name": "primary"},
    "PR": {"mt": "460", "name": "primary"},
}

## The MT number allocation and directory name for NU (neutron observables) data
mt_nu_sf5 = {
    "": {"mt": "452", "name": ""},
    "PR": {"mt": "456", "name": "prompt"},
    "SEC": "",
    "SEC/PR": {"mt": None, "name": "miscellaneous"},
    "DL": {"mt": "455", "name": "delayed"},
    "TER": {"mt": "456", "name": "prompt"},
    "DL/CUM": {"mt": "455", "name": "delayed"},
    "DL/GRP": {"mt": "455", "name": "delayed"},
    "PR/TER": {"mt": None, "name": "miscellaneous"},
    "PRE/PR": {"mt": None, "name": "miscellaneous"},
    "SEC/PR": {"mt": None, "name": "miscellaneous"},
    "PRE/PR/FRG": {"mt": None, "name": "miscellaneous"},
    "PR/FRG": {"mt": None, "name": "miscellaneous"},
    "PR/PAR": {"mt": None, "name": "miscellaneous"},
    "PR/NUM": {"mt": None, "name": "miscellaneous"},
    "NUM": {"mt": None, "name": "miscellaneous"},
}

## Previous mf3.json in MT_PATH_JSON
sf3_dict = {
    "TOT": {"mt": "1", "reaction": "(n,total)", "sf5-8": None},
    "EL": {"mt": "2", "reaction": "(n,elas.)", "sf5-8": None},
    "NON": {"mt": "3", "reaction": "(n,nonelas.)", "sf5-8": None},
    "INL": {"mt": "4", "reaction": "(n,inelas.)", "sf5-8": "SIG"},
    "F": {"mt": "18", "reaction": "(n,f)", "sf5-8": None},
    "G": {"mt": "102", "reaction": "(n,g)", "sf5-8": None},
    "P": {"mt": "103", "reaction": "(n,p)", "sf5-8": None},
    "D": {"mt": "104", "reaction": "(n,d)", "sf5-8": None},
    "T": {"mt": "105", "reaction": "(n,t)", "sf5-8": None},
    "HE3": {"mt": "106", "reaction": "(n,h)", "sf5-8": None},
    "A": {"mt": "107", "reaction": "(n,a)", "sf5-8": None},
    "ABS": {"mt": "27", "reaction": "(n,abs)", "sf5-8": None},
    "2N": {"mt": "16", "reaction": "(n,2n)", "sf5-8": None},
    "3N": {"mt": "17", "reaction": "(n,3n)", "sf5-8": None},
    "FIS": {"mt": "19", "reaction": "(n,0f)", "sf5-8": "first"},
    "N+F": {"mt": "20", "reaction": "(n,nf)", "sf5-8": "2nd"},
    "2N+F": {"mt": "21", "reaction": "(n,2nf)", "sf5-8": "3rd"},
    "3N+F": {"mt": "38", "reaction": "(n,3nf)", "sf5-8": "4th"},
    "X+N": {"mt": "201", "reaction": "(n,Xn)", "sf5-8": None},
    "X+G": {"mt": "202", "reaction": "(n,Xg)", "sf5-8": None},
    "X+P": {"mt": "203", "reaction": "(n,Xp)", "sf5-8": None},
    "X+D": {"mt": "205", "reaction": "(n,Xt)", "sf5-8": None},
    "X+HE3": {"mt": "206", "reaction": "(n,Xh)", "sf5-8": None},
    "X+A": {"mt": "207", "reaction": "(n,Xa)", "sf5-8": None},
    "N+A": {"mt": "22", "reaction": "(n,na)", "sf5-8": None},
    "N+3A": {"mt": "23", "reaction": "(n,n3a)", "sf5-8": None},
    "N+P": {"mt": "28", "reaction": "(n,np)", "sf5-8": None},
    "N+2A": {"mt": "29", "reaction": "(n,n2a)", "sf5-8": None},
    "N+D": {"mt": "32", "reaction": "(n,nd)", "sf5-8": None},
    "N+T": {"mt": "33", "reaction": "(n,nt)", "sf5-8": None},
    "N+H": {"mt": "34", "reaction": "(n,nh)", "sf5-8": None},
    "N+D+2A": {"mt": "35", "reaction": "(n,nd2a)", "sf5-8": None},
    "N+T+2A": {"mt": "36", "reaction": "(n,nt2a)", "sf5-8": None},
    "N+2P": {"mt": "44", "reaction": "(n,n2p)", "sf5-8": None},
    "N+P+A": {"mt": "45", "reaction": "(n,npa)", "sf5-8": None},
    "2N+A": {"mt": "24", "reaction": "(n,2na)", "sf5-8": None},
    "2N+D": {"mt": "11", "reaction": "(n,2nd)", "sf5-8": None},
    "2N+2A": {"mt": "30", "reaction": "(n,2n2a)", "sf5-8": None},
    "2N+P": {"mt": "41", "reaction": "(n,2np)", "sf5-8": None},
    "2N+T": {"mt": "154", "reaction": "(n,2nt)", "sf5-8": None},
    "2N+2P": {"mt": "190", "reaction": "(n,2n2p)", "sf5-8": None},
    "2N+P+A": {"mt": "159", "reaction": "(n,2npa)", "sf5-8": None},
    "3N+A": {"mt": "25", "reaction": "(n,3na)", "sf5-8": None},
    "3N+P": {"mt": "42", "reaction": "(n,3np)", "sf5-8": None},
    "3N+D": {"mt": "157", "reaction": "(n,3nd)", "sf5-8": None},
    "2A": {"mt": "108", "reaction": "(n,2a)", "sf5-8": None},
    "3A": {"mt": "109", "reaction": "(n,3a)", "sf5-8": None},
    "2P": {"mt": "111", "reaction": "(n,2p)", "sf5-8": None},
    "P+A": {"mt": "112", "reaction": "(n,pa)", "sf5-8": None},
    "T+2A": {"mt": "113", "reaction": "(n,t2a)", "sf5-8": None},
    "D+2A": {"mt": "114", "reaction": "(n,d2a)", "sf5-8": None},
    "P+D": {"mt": "115", "reaction": "(n,pd)", "sf5-8": None},
    "P+T": {"mt": "116", "reaction": "(n,pt)", "sf5-8": None},
    "D+A": {"mt": "117", "reaction": "(n,da)", "sf5-8": None},
    "4N": {"mt": "37", "reaction": "(n,4n)", "sf5-8": None},
    "4N+P": {"mt": "156", "reaction": "(n,4np)", "sf5-8": None},
    "5N": {"mt": "152", "reaction": "(n,5n)", "sf5-8": None},
    "6N": {"mt": "153", "reaction": "(n,6n)", "sf5-8": None},
    "T+A": {"mt": "155", "reaction": "(n,ta)", "sf5-8": None},
    "N+D+A": {"mt": "158", "reaction": "(n,n'da)", "sf5-8": None},
    "7N": {"mt": "160", "reaction": "(n,7n)", "sf5-8": None},
    "8N": {"mt": "161", "reaction": "(n,8n)", "sf5-8": None},
    "5N+P": {"mt": "162", "reaction": "(n,5np)", "sf5-8": None},
    "6N+P": {"mt": "163", "reaction": "(n,6np)", "sf5-8": None},
    "7N+P": {"mt": "164", "reaction": "(n,7np)", "sf5-8": None},
    "4N+A": {"mt": "165", "reaction": "(n,4na)", "sf5-8": None},
    "5N+A": {"mt": "166", "reaction": "(n,5na)", "sf5-8": None},
    "6N+A": {"mt": "167", "reaction": "(n,6na)", "sf5-8": None},
    "7N+A": {"mt": "168", "reaction": "(n,7na)", "sf5-8": None},
    "4N+D": {"mt": "169", "reaction": "(n,4nd)", "sf5-8": None},
    "5N+D": {"mt": "170", "reaction": "(n,5nd)", "sf5-8": None},
    "6N+D": {"mt": "171", "reaction": "(n,6nd)", "sf5-8": None},
    "3N+T": {"mt": "172", "reaction": "(n,3nt)", "sf5-8": None},
    "4N+T": {"mt": "173", "reaction": "(n,4nt)", "sf5-8": None},
    "5N+T": {"mt": "174", "reaction": "(n,5nt)", "sf5-8": None},
    "6N+T": {"mt": "175", "reaction": "(n,6nt)", "sf5-8": None},
    "2N+HE3": {"mt": "176", "reaction": "(n,2nh)", "sf5-8": None},
    "3N+HE3": {"mt": "177", "reaction": "(n,3nh)", "sf5-8": None},
    "4N+HE3": {"mt": "178", "reaction": "(n,4nh)", "sf5-8": None},
    "3N+2P": {"mt": "179", "reaction": "(n,3n2p)", "sf5-8": None},
    "3N+2": {"mt": "180", "reaction": "(n,3n2a)", "sf5-8": None},
    "3N+P+A": {"mt": "181", "reaction": "(n,3npa)", "sf5-8": None},
    "D+T": {"mt": "182", "reaction": "(n,dt)", "sf5-8": None},
    "N+P+D": {"mt": "183", "reaction": "(n,n'pd)", "sf5-8": None},
    "N+P+T": {"mt": "184", "reaction": "(n,n'pt)", "sf5-8": None},
    "N+D+T": {"mt": "185", "reaction": "(n,n'dt)", "sf5-8": None},
    "N+P+HE3": {"mt": "186", "reaction": "(n,n'ph)", "sf5-8": None},
    "N+D+HE3": {"mt": "187", "reaction": "(n,n'dh)", "sf5-8": None},
    "N+T+HE3": {"mt": "188", "reaction": "(n,n'th)", "sf5-8": None},
    "N+T+A": {"mt": "189", "reaction": "(n,n'ta)", "sf5-8": None},
    "P+HE3": {"mt": "191", "reaction": "(n,ph)", "sf5-8": None},
    "D+HE": {"mt": "192", "reaction": "(n,dh)", "sf5-8": None},
    "HE+A": {"mt": "193", "reaction": "(n,ha)", "sf5-8": None},
    "4N+2P": {"mt": "194", "reaction": "(n,4n2p)", "sf5-8": None},
    "4N+2A": {"mt": "195", "reaction": "(n,4n2a)", "sf5-8": None},
    "4N+P+A": {"mt": "196", "reaction": "(n,4npa)", "sf5-8": None},
    "3P": {"mt": "197", "reaction": "(n,3p)", "sf5-8": None},
    "N+3P": {"mt": "198", "reaction": "(n,n'3p)", "sf5-8": None},
    "3N+2P+A": {"mt": "199", "reaction": "(n,3n2pa)", "sf5-8": None},
    "5N+2P": {"mt": "200", "reaction": "(n,5n2p)", "sf5-8": None},
    "X": {"mt": "10", "reaction": "(n,contin.)", "sf5-8": "CON,SIG"},
}

mt_range = {
    "N": list(range(50, 92)),
    "P": list(range(600, 649)),
    "D": list(range(650, 699)),
    "T": list(range(700, 749)),
    "H": list(range(750, 799)),
    "A": list(range(800, 849)),
    "G": list(range(102)),
}

def get_unique_mf_mt(df2):

    if len(df2["mt"].unique()) == 0:
        mt = None
    else:
        mt = df2["mt"].unique()[0]

    if len(df2["mf"].unique()) == 0:
        mf = None
    else:
        mf = df2["mf"].unique()[0]

    return mf, mt


def get_mf(react_dict):

    if sf_to_mf.get(react_dict["sf6"]):
        if react_dict["sf6"] == "NU":
            return int(sf_to_mf[react_dict["sf6"]])

        elif react_dict["sf4"] == "0-G-0":
            return 12  # Multiplicity of photon production

        else:
            return int(sf_to_mf[react_dict["sf6"]])

    else:
        return 9999


def get_mt(react_dict):

    if react_dict["sf6"] == "FY":
        return (
            int(mt_fy_sf5[react_dict["sf5"]]["mt"])
            if react_dict["sf5"] and mt_fy_sf5.get(react_dict["sf5"])
            else None
        )

    elif react_dict["sf6"] == "NU":
        return (
            int(mt_nu_sf5[react_dict["sf5"]]["mt"])
            if react_dict["sf5"]
            and mt_nu_sf5.get(react_dict["sf5"])
            and mt_nu_sf5[react_dict["sf5"]]["mt"]
            else None
        )

    else:
        if react_dict["process"] == "N,INL":
            return 4

        elif (
            react_dict["process"].split(",")[0] != "N"
            and react_dict["process"].split(",")[1] == "N"
        ):
            return 4

        else:
            return (
                int(sf3_dict[react_dict["process"].split(",")[1]]["mt"])
                if react_dict["process"]
                and sf3_dict.get(react_dict["process"].split(",")[1])
                else None
            )


def e_lvl_to_mt(level_num, process):
    ## This is definition of outgoing particle
    ## N,INL = 4
    ## N,G = 102
    ## N,P = 103  --> N,P or P,P to the excitation states are MT=600-649
    inc_part, out_part = process.split(",")

    if not out_part in sf3_dict.keys():
        return None
    
    if out_part == "INL":
        out_part = inc_part


    if level_num is None:
        return None 

    elif not out_part in mt_range:
        return None

    elif int(level_num) < len(mt_range[out_part]):
        return int(mt_range[out_part][int(level_num)])

    else:
        return max(mt_range[out_part])


# def mt_to_reaction():
#     with open( MT_DEF ) as f:
#         lines = f.readlines()

#     # mt_dict = {}
#     sf3_dict = {}
#     for line in lines:
#         if line.startswith("#"):
#             continue

#         ## #MT        Reaction             SF3            SF5-8            comment
#         ## 1           (n,total)           TOT
#         data = line.strip().split()

#         # mt_dict[data[0]] = {}
#         # mt_dict[data[0]]["reaction"] = data[1] if len(data) >= 2 else None
#         # mt_dict[data[0]]["sf3"] = data[2] if len(data) >= 3 else None
#         # mt_dict[data[0]]["sf5-8"] = data[3] if len(data) >= 4 else None

#         sf3_dict[data[2]] = {}  # if len(data) >= 3 else None: {} }
#         sf3_dict[data[2]]["mt"] = data[0]
#         sf3_dict[data[2]]["reaction"] = data[1] if len(data) >= 2 else None
#         sf3_dict[data[2]]["sf5-8"] = data[3] if len(data) >= 4 else None

#     return sf3_dict


# def read_mt_json():
#     if os.path.exists(MF3_JSON):
#         with open(MF3_JSON) as map_file:
#             return json.load(map_file)

# sf3_dict = read_mt_json()
