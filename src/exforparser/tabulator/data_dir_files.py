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
import re
from exforparser.config import OUT_PATH
from exforparser.submodules.utilities.reaction import sf6_to_dir


PARTICLE_PROJECTILE_DIRS = {
    "0": "0",
    "A": "a",
    "D": "d",
    "E": "e",
    "G": "g",
    "H": "h",
    "HE3": "h",
    "N": "n",
    "P": "p",
    "T": "t",
}


def nuclide_reformat(code):
    value = str(code)
    parts = value.split("-")
    if len(parts) >= 3 and parts[0].isdigit() and int(parts[0]) > 0:
        nuclide = parts[1].capitalize() + "-" + parts[2]
        if len(parts) > 3:
            nuclide += "-" + "-".join(parts[3:])
        return nuclide

    match = re.fullmatch(r"([A-Za-z]{1,3})-?(\d+)(?:-(.+))?", value)
    if not match:
        return value
    element, mass, state = match.groups()
    nuclide = f"{element.capitalize()}-{mass}"
    return f"{nuclide}-{state}" if state else nuclide


def projectile_reformat(projectile):
    projectile = str(projectile).upper()
    if projectile in PARTICLE_PROJECTILE_DIRS:
        return PARTICLE_PROJECTILE_DIRS[projectile]
    return nuclide_reformat(projectile)


def is_particle_projectile(projectile):
    return str(projectile).upper() in PARTICLE_PROJECTILE_DIRS


def is_ion_projectile(projectile):
    """Return whether *projectile* is a nuclide-coded heavy ion."""
    projectile = str(projectile).upper()
    if is_particle_projectile(projectile):
        return False
    parts = projectile.split("-")
    if len(parts) < 3 or not parts[0].isdigit() or not parts[2].isdigit():
        return False

    charge = int(parts[0])
    mass = int(parts[2])
    return charge > 2 or (charge == 2 and mass > 4)


def uses_ion_output_layout(projectile):
    """Return whether *projectile* belongs under the Heavy Ion tree."""
    return is_ion_projectile(projectile)


def target_reformat(react_dict):
    return nuclide_reformat(react_dict["target"])


def process_reformat(react_dict):
    projectile = react_dict["process"].split(",")[0]
    if is_particle_projectile(projectile):
        return projectile_reformat(projectile)
    if is_ion_projectile(projectile):
        return "ion"
    return projectile.lower()


def reaction_reformat(react_dict):
    projectile, outgoing = react_dict["process"].split(",", 1)
    return f"{projectile_reformat(projectile)}-{outgoing.lower()}"


def level_num_reformat(level_num):
    return str(int(level_num))


def get_dir_name(type, react_dict, level_num=None, subdir=None):
    ### generate output dir and filename
    if type == "exfortables_py" and uses_ion_output_layout(
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
                else f"{outgoing}-L{level_num_reformat(level_num)}"
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
            reaction_reformat(react_dict)
            if not level_num
            else (
                f"{reaction_reformat(react_dict)}"
                f"-L{level_num_reformat(level_num)}"
            )
        ),
        sf6_to_dir[react_dict["sf6"]] if react_dict.get("sf6") else "",
        subdir if subdir else "",
    )


def exfortables_filename(dir, exfor_id, process, react_dict, bib, en=None, prod=None):
    product = nuclide_reformat(prod) if prod else None
    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + (product + "_" if product else "")
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
    product = nuclide_reformat(prod)
    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + product
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
    product = nuclide_reformat(prod)
    return os.path.join(
        dir,
        (
            target_reformat(react_dict)
            + "_"
            + process
            + "_"
            + product
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
    projectile, outgoing = react_dict["process"].split(",", 1)
    if uses_ion_output_layout(projectile):
        return os.path.join(
            OUT_PATH,
            "exfortables_py",
            "ion",
            target_reformat(react_dict),
            projectile_reformat(projectile),
            outgoing.lower(),
            obs_type,
        )

    return os.path.join(
        OUT_PATH,
        "exfortables_py",
        process_reformat(react_dict),
        target_reformat(react_dict),
        reaction_reformat(react_dict),
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
        (target_reformat(react_dict) + ".txt"),
    )


# --------------------- Resonance Parameter
def get_resonance_param_dir_name(obs_type, react_dict):
    """Directory for resonance parameter files under the exfortables_py tree.

    Produces: <OUT_PATH>/exfortables_py/<projectile>/<target>/<process>/resonance_parameter/<sf6>/<sf8>/
    """
    projectile, outgoing = react_dict.get("process", "N,0").split(",", 1)
    if uses_ion_output_layout(projectile):
        return os.path.join(
            OUT_PATH,
            "exfortables_py",
            "ion",
            target_reformat(react_dict),
            projectile_reformat(projectile),
            outgoing.lower(),
            "resonance_parameter",
            react_dict["sf6"].replace("/", "-"),
            react_dict["sf8"].replace("/", "-") if react_dict.get("sf8") else "",
        )

    return os.path.join(
        OUT_PATH,
        "exfortables_py",
        process_reformat(react_dict),
        target_reformat(react_dict),
        reaction_reformat(react_dict),
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
        target_reformat(react_dict)
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
