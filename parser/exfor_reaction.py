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


from pyparsing import *

from .exfor_field import parse_parenthesis, parentheses


def split_sf(sf49):
    if sf49:
        sf4 = len(sf49) > 0 and sf49[0] or None
        sf5 = len(sf49) > 1 and sf49[1] or None
        sf6 = len(sf49) > 2 and sf49[2] or None
        sf7 = len(sf49) > 3 and sf49[3] or None
        sf8 = len(sf49) > 4 and sf49[4] or None
        sf9 = len(sf49) > 5 and sf49[5] or None
    return {
        "sf4": sf4,
        "sf5": sf5,
        "sf6": sf6,
        "sf7": sf7,
        "sf8": sf8,
        "sf9": sf9,
    }


def parse_primitive_reaction(reaction_field) -> dict:
    for pointer, p_block in reaction_field.items():
        flat_reaction = "".join(p_block)
        # a = parentheses.parse_string(flat_reaction)
        # b = free_text.parse_string("".join(p_block))
        return parentheses.parse_string(flat_reaction)


def get_details(bb):
    dict = {
        "target": bb[0],
        "process": bb[1][0],
        "sf49": bb[2],
    }
    dict.update(split_sf(bb[2].split(",")))

    return dict


def parse_reaction(reaction_field) -> dict:

    dict = {}

    for pointer, p_block in reaction_field.items():

        flat_reaction_str = "".join(p_block)

        ## parse locations of parentheses
        c, d = parse_parenthesis(flat_reaction_str, 0)

        x4_code = flat_reaction_str[c[0] : d[-1] + 1]
        free_text = flat_reaction_str[d[-1] + 1 :]

        b = parentheses.parse_string(x4_code).as_list()

        if x4_code.startswith("((("):
            try:
                reaction_info = {
                    "x4_code": x4_code,
                    0: {"code": b[0][0][0], "type": b[0][0][1]},
                    1: {"code": b[0][0][2], "type": b[0][0][1]},
                    2: {"code": b[0][2][0], "type": b[0][2][1]},
                    3: {"code": b[0][2][2], "type": b[0][2][1]},
                    "type": b[0][1],
                    "free_text": free_text,
                }

                reaction_info[0].update(get_details(b[0][0][0]))
                reaction_info[1].update(get_details(b[0][0][2]))
                reaction_info[2].update(get_details(b[0][2][0]))
                reaction_info[3].update(get_details(b[0][2][2]))

            except:
                reaction_info = {
                    "x4_code": x4_code,
                    0: {"code": b[0], "type": None},
                    "type": "?",
                    "free_text": free_text,
                }

        elif x4_code.startswith("(("):
            try:
                reaction_info = {
                    "x4_code": x4_code,
                    0: {"code": b[0][0], "type": None},
                    1: {"code": b[0][2], "type": None},
                    "type": b[0][1],
                    "free_text": free_text,
                }
                reaction_info[0].update(get_details(b[0][0]))
                reaction_info[1].update(get_details(b[0][2]))

            except:
                reaction_info = {
                    "x4_code": x4_code,
                    0: {"code": b[0], "type": None},
                    "type": "/",
                    "free_text": free_text,
                }

        else:
            reaction_info = {
                "x4_code": x4_code,
                0: {"code": b[0], "type": None},
                "type": None,
                "free_text": free_text,
            }
            reaction_info[0].update(get_details(b[0]))

        dict[pointer] = reaction_info

    return dict
