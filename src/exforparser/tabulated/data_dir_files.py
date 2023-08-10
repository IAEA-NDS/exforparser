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
import os
from ..config import OUT_PATH
from .exfor_reaction_mt import sf6_to_dir


def target_reformat(react_dict):

    if len(react_dict["target"].split("-")) == 3:
        target = (
            react_dict["target"].split("-")[1].capitalize()
            + "-"
            + react_dict["target"].split("-")[2]
        )

    else:
        target = (
            react_dict["target"].split("-")[1].capitalize()
            + "-"
            + react_dict["target"].split("-")[2]
            + "-"
            + react_dict["target"].split("-")[3].lower()
        )

    return target


def process_reformat(react_dict):
    if len(react_dict["process"].split(",")[0]) == 1:
        return react_dict["process"].split(",")[0].lower()

    elif "-" in react_dict["process"].split(",")[0]:
        return (
            "i/"
            + react_dict["process"].split(",")[0].split("-")[1].capitalize()
            + react_dict["process"].split(",")[0].split("-")[2]
        )

    else:
        return "i/" + react_dict["process"].split(",")[0]


def get_dir_name(react_dict, level_num=None, subdir=None):
    ### generate output dir and filename

    return os.path.join(
        OUT_PATH,
        "exfortables",
        process_reformat(react_dict),
        target_reformat(react_dict),
        react_dict["process"].replace(",", "-").lower()
            if not level_num
            else react_dict["process"].replace(",", "-").lower()
            + "-"
            + "L"
            + str(level_num),
        sf6_to_dir[react_dict["sf6"]],
        subdir if subdir else "",
    )


def exfortables_filename(dir, id, process, react_dict, bib, en=None, prod=None):

    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + (str(prod) + "_" if prod else "")
            + ("E" + "{:.3e}".format(en) + "_" if en else "")
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "-"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )


def exfortables_filename_product(dir, id, process, prod, react_dict, bib):

    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + str(prod)
            + "_"
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "-"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )


def exfortables_filename_Einc_prodocut(dir, id, process, en, prod, react_dict, bib):

    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + str(prod)
            + "_"
            + "E"
            + "{:.3e}".format(en)
            + "_"
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "-"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )


def exfortables_filename_Einc(dir, id, process, en, react_dict, bib):

    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + "E"
            + "{:.3e}".format(en)
            + "_"
            + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + "-"
            + str(id)
            + "-"
            + (
                bib["references"][0]["publication_year"]
                if bib.get("references")
                else "1900"
            )
            + ".txt"
        ),
    )
