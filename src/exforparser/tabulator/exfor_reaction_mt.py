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
