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


LIGHT_ION_PROJECTILES = {
    "P": "p",
    "D": "d",
    "T": "t",
    "A": "a",
    "HE3": "He-3",
}


def nuclide_reformat(code):
    parts = str(code).split("-")
    if len(parts) >= 3 and parts[0].isdigit():
        nuclide = parts[1].capitalize() + "-" + parts[2]
        if len(parts) > 3:
            nuclide += "-" + parts[3].lower()
        return nuclide
    return str(code)


def projectile_reformat(projectile):
    projectile = str(projectile).upper()
    if projectile in LIGHT_ION_PROJECTILES:
        return LIGHT_ION_PROJECTILES[projectile]
    return nuclide_reformat(projectile)


def is_ion_projectile(projectile):
    projectile = str(projectile).upper()
    if projectile in LIGHT_ION_PROJECTILES:
        return True
    if projectile in ("0", "N", "G"):
        return False
    parts = projectile.split("-")
    return len(parts) >= 3 and parts[0].isdigit() and int(parts[0]) > 0


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
    if type == "exfortables_py" and is_ion_projectile(
        react_dict["process"].split(",")[0]
    ):
        outgoing = react_dict["process"].split(",", 1)[1].lower()
        return os.path.join(
            OUT_PATH,
            type,
            "ion",
            target_reformat(react_dict),
            projectile_reformat(react_dict["process"].split(",")[0]),
            (
                outgoing
                if not level_num
                else f"{outgoing}-L{str(int(level_num))}"
            ),
            sf6_to_dir[react_dict["sf6"]] if react_dict.get("sf6") else "",
            subdir if subdir else "",
        )

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


# --------------------- For observables (thermal, macs, resonance_integral, etc.)


def get_obs_dir_name(obs_type, react_dict):
    """Directory for tabular observables under the exfortables_py tree.

    Produces: <OUT_PATH>/exfortables_py/<projectile>/<target>/<process>/<obs_type>/
    e.g.      .../exfortables_py/n/U-235/n-g/thermal/
    """
    return os.path.join(
        OUT_PATH,
        "exfortables_py",
        process_reformat(react_dict),
        target_reformat(react_dict),
        react_dict["process"].replace(",", "-").lower(),
        obs_type,
    )


def get_reference_obs_dir_name(obs_type, react_dict):
    """Directory for legacy thermal/resonance observable tables.

    These outputs may include reference/evaluated comparison data.  Keep them
    outside exfortables_py, which is reserved for pure EXFOR exports.
    """
    root = "thermal" if obs_type == "thermal" else os.path.join("resonance_data", obs_type)
    return os.path.join(
        OUT_PATH,
        root,
        process_reformat(react_dict),
        target_reformat(react_dict),
        react_dict["process"].replace(",", "-").lower(),
    )


def get_thermal_filename(dir, react_dict):
    return os.path.join(
        dir,
        (react_dict["target"] + ".txt"),
    )


# --------------------- Resonance Parameter
def get_resonance_param_dir_name(obs_type, react_dict):
    """Directory for resonance parameter files under the exfortables_py tree.

    Produces: <OUT_PATH>/exfortables_py/<projectile>/<target>/<process>/resonance_parameter/<sf6>/<sf8>/
    """
    return os.path.join(
        OUT_PATH,
        "exfortables_py",
        react_dict["projectile"].lower(),
        target_reformat(react_dict),
        react_dict.get("process", "n-0").replace(",", "-").lower(),
        "resonance_parameter",
        react_dict["sf6"].replace("/", "-"),
        react_dict["sf8"].replace("/", "-") if react_dict.get("sf8") else "",
    )


def get_reference_resonance_param_dir_name(react_dict):
    """Directory for legacy resonance-parameter tables with comparison context."""
    return os.path.join(
        OUT_PATH,
        "resonance_data",
        "resonance_parameter",
        react_dict["projectile"].lower(),
        target_reformat(react_dict),
        react_dict.get("process", "n-0").replace(",", "-").lower(),
        react_dict["sf6"].replace("/", "-"),
        react_dict["sf8"].replace("/", "-") if react_dict.get("sf8") else "",
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


def write_list_files(root=None):
    """Scan the output tree and write a <dirname>.list index file in each
    leaf directory that contains .txt data files.

    Each line in the .list file has the format:
        <filename>\t<row_count>
    where <row_count> is the number of data rows (lines that are not
    blank and do not start with '#').

    Args:
        root: directory to scan; defaults to OUT_PATH.
    """
    if root is None:
        root = OUT_PATH

    for dirpath, dirnames, filenames in os.walk(root):
        txt_files = sorted(f for f in filenames if f.endswith(".txt"))
        if not txt_files:
            continue
        list_name = os.path.basename(dirpath) + ".list"
        list_path = os.path.join(dirpath, list_name)
        with open(list_path, "w") as lf:
            for fname in txt_files:
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath) as df:
                        count = sum(
                            1 for line in df
                            if line.strip() and not line.startswith("#")
                        )
                except OSError:
                    count = 0
                lf.write(f"{fname}\t{count}\n")
