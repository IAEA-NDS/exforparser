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
from exforparser.config import OUT_PATH
from exforparser.submodules.utilities.reaction import sf6_to_dir


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

    return str(target)


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


def get_dir_name(type, react_dict, level_num=None, subdir=None):
    ### generate output dir and filename

    return os.path.join(
        OUT_PATH,
        type,
        process_reformat(react_dict),
        target_reformat(react_dict),
        (
            react_dict["process"].replace(",", "-").lower()
            if not level_num
            else f"{react_dict['process'].replace(',', '-').lower()}-L{str(int(level_num))}"
        ),
        sf6_to_dir[react_dict["sf6"]] if react_dict.get("sf6") else "",
        subdir if subdir else "",
    )


def exfortables_filename(dir, exfor_id, process, react_dict, bib, en=None, prod=None):

    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + (str(prod) + "_" if prod else "")
            + ("E" + "{:.3e}".format(en) + "_" if en else "")
            # + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + bib["first_author"]
            + "-"
            + str(exfor_id)
            + "-"
            + (
                # bib["references"][0]["publication_year"]
                # if bib.get("references")
                str(bib["year"])
                if bib.get("year")
                else "1900"
            )
            + ".txt"
        ),
    )


def exfortables_filename_product(dir, exfor_id, process, prod, react_dict, bib):

    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + str(prod)
            + "_"
            # + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + bib["first_author"]
            + "-"
            + str(exfor_id)
            + "-"
            + (
                # bib["references"][0]["publication_year"]
                # if bib.get("references")
                str(bib["year"])
                if bib.get("year")
                else "1900"
            )
            + ".txt"
        ),
    )


def exfortables_filename_Einc_prodocut(
    dir, exfor_id, process, en, prod, react_dict, bib
):

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
            # + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + bib["first_author"]
            + "-"
            + str(exfor_id)
            + "-"
            + (
                # bib["references"][0]["publication_year"]
                # if bib.get("references")
                bib["year"]
                if bib.get("year")
                else "1900"
            )
            + ".txt"
        ),
    )


def exfortables_filename_Einc(dir, exfor_id, process, en, react_dict, bib):

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
            # + bib["authors"][0]["name"].split(".")[-1].replace(" ", "")
            + bib["first_author"]
            + "-"
            + str(exfor_id)
            + "-"
            + (
                # bib["references"][0]["publication_year"]
                # if bib.get("references")
                bib["year"]
                if bib.get("year")
                else "1900"
            )
            + ".txt"
        ),
    )


# --------------------- For observables


def get_thermal_dir_name(obs_type, react_dict):
    ### generate output dir and filename

    return os.path.join(
        OUT_PATH, obs_type, react_dict["process"].replace(",", "-").lower()
    )


def get_thermal_filename(dir, react_dict):
    return os.path.join(
        dir,
        (react_dict["target"] + ".txt"),
    )


# --------------------- Resonance Parameter
def get_resonance_param_dir_name(obs_type, react_dict):
    ### generate output dir and filename

    return os.path.join(
        OUT_PATH,
        obs_type,
        react_dict["projectile"],
        target_reformat(react_dict),
        react_dict["sf6"].replace("/", "-"),
        react_dict["sf8"].replace("/", "-") if react_dict.get("sf8") else None,
    )


def get_resonance_param_file_name(dir, exfor_id, bib, react_dict):
    ### generate output dir and filename

    return os.path.join(
        dir,
        react_dict["target"]
        + "_"
        + bib["first_author"]
        + "-"
        + str(exfor_id)
        + "_"
        + (str(bib["year"]) if bib.get("year") else "1900")
        + ".txt",
    )
