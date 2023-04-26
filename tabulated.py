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
import random
import pandas as pd
import logging


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logging.basicConfig(filename="tabulated.log", level=logging.DEBUG, filemode="w")

from config import OUT_PATH
from utilities.utilities import dict_merge, del_outputs, print_time
from exparser import convert_exfor_to_json, write_dict_to_json
from parser.list_x4files import list_entries_from_df
from parser.exfor_unit import unify_units
from tabulated.exfor_reaction_mt import (
    sf3_dict,
    mt_fy,
    rp_sig,
    mt_nu_sf5,
    get_mf,
    get_mt,
)

from tabulated.data_write import *
from tabulated.data_dir_files import *
from tabulated.data_process import *
from sql.creation import *

# initialize exfor_dictionary
from exfor_dictionary.exfor_dictionary import Diction
D = Diction()

# get heading list
x_en_heads = D.get_incident_en_heads()
x_en_err_heads = D.get_incident_en_err_heads()
x_data_heads = D.get_data_heads()
x_data_err_heads = D.get_data_err_heads()


def reaction_ditc(entry_id, entry_json, level_num, df):
    entnum, subent, pointer = entry_id.split("-")
    react_dict = entry_json["reactions"][subent][pointer]["children"][0]
    reac_data = [
        {
            "entry_id": entry_id,
            "entry": entnum,
            "target": react_dict["target"],
            "projectile": react_dict["process"].split(",")[0],
            "process": react_dict["process"],
            "sf4": react_dict["sf4"],
            "residual": df["residual"],
            "level_num": level_num,
            "e_inc_min": df["en_inc"].min(),
            "e_inc_max": df["en_inc"].max(),
            "points": len(df.index),
            "sf5": react_dict["sf5"],
            "sf6": react_dict["sf6"],
            "sf7": react_dict["sf7"],
            "sf8": react_dict["sf8"],
            "sf9": react_dict["sf9"],
            "x4_code": entry_json["reactions"][subent][pointer]["x4_code"],
        }
    ]
    insert_reaction(reac_data)


def tabulated_to_exfortables_format(id, entry_json, data_dict_conv):
    entnum = id[0:5]
    subent = id[5:8]

    for pointer in entry_json["reactions"][subent]:
        df = pd.DataFrame()
        entry_id = entnum + "-" + subent + "-" + pointer
        print(entry_id)

        if entry_json["reactions"][subent][pointer]["type"] is not None:
            ## if ratio or any other complex reactions, it will be skipped so far
            continue

        react_dict = entry_json["reactions"][subent][pointer]["children"][0]

        ## ------------------------  Case for the cross section measuements ------------------------  ##
        if react_dict["sf6"] == "SIG":
            if (
                not any(
                    par == react_dict["process"].split(",")[1]
                    for par in sf3_dict.keys()
                )
                or any(
                    excep in react_dict["sf8"]
                    for excep in ["MSC", "REL", "FRC", "RES", "RAW"]
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            if react_dict["sf5"] is None or any(
                sf5 == react_dict["sf5"] for sf5 in rp_sig.keys()
            ):

                df = process_general(entry_id, entry_json, data_dict_conv)
                if df["en_inc"].isnull().values.all():
                    continue
                mf = get_mf(react_dict)
                mt = get_mt(react_dict)
                dir = get_dir_name(react_dict, level_num=None, subdir=None)

                if any(
                    r == react_dict["process"].split(",")[1]
                    for r in ("F", "TOT", "NON", "ABS")
                ) or (
                    react_dict["target"].split("-")[2] == "0"
                    and react_dict["sf4"] is None
                ):

                    ## no reaction product would be given in these cases
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower(),
                        react_dict,
                        entry_json["bib_record"],
                        None,
                        None,
                    )
                    write_to_exfortables_format_sig(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df,
                    )

                else:
                    for prod in df["residual"].unique():
                        df2 = df[df["residual"] == prod]
                        filename = exfortables_filename(
                            dir,
                            entry_id,
                            react_dict["process"].replace(",", "-").lower(),
                            react_dict,
                            entry_json["bib_record"],
                            None,
                            prod,
                        )
                        write_to_exfortables_format_sig(
                            entry_id,
                            dir,
                            filename,
                            entry_json["bib_record"],
                            react_dict,
                            mf + " - " + str(mt),
                            df2,
                        )

            elif (
                react_dict["sf5"]
                == "PAR"
            ):
                ## none of (N,NON) PAR,SIG are useful
                df = process_general(entry_id, entry_json, data_dict_conv)
                if df["en_inc"].isnull().values.all():
                    continue
                mf = get_mf(react_dict)

                for level_num in df["level_num"].unique():
                    df2 = df[df["level_num"] == level_num]
                    mt = df2["mt"].unique()

                    if not level_num:
                        level_num = 0
                        mt = "99"

                    dir = get_dir_name(react_dict, level_num=level_num, subdir=None)
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower()
                        + "-L"
                        + str(level_num),
                        react_dict,
                        entry_json["bib_record"],
                        None,
                        (
                            react_dict["target"].split("-")[1].capitalize()
                            + react_dict["target"].split("-")[2]
                            if len(react_dict["target"].split("-")) == 3
                            else react_dict["target"].split("-")[1].capitalize()
                            + react_dict["target"].split("-")[2]
                            + react_dict["target"].split("-")[3].lower()
                        ),
                    )
                    write_to_exfortables_format_sig(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df2,
                    )

        ## ------------------------  Case for the angular distributions ------------------------  ##
        elif react_dict["sf6"] == "DA":
            if (
                not any(
                    par == react_dict["process"].split(",")[1]
                    for par in sf3_dict.keys()
                )
                or any(
                    react_dict["sf8"] != excep for excep in ("EXP") if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            if react_dict["sf5"] is None or any(
                sf5 == react_dict["sf5"] for sf5 in rp_sig.keys()
            ):

                df = process_general(entry_id, entry_json, data_dict_conv)
                if df["en_inc"].isnull().values.all():
                    continue
                mf = get_mf(react_dict)
                mt = get_mt(react_dict)
                dir = get_dir_name(react_dict, level_num=None, subdir=None)

                for en in df["en_inc"].unique():
                    df2 = df[df["en_inc"] == en]

                    if (
                        react_dict["target"].split("-")[2] == "0"
                        and react_dict["sf4"] is None
                    ):
                        ## case for ,DA without product
                        filename = exfortables_filename(
                            dir,
                            entry_id,
                            react_dict["process"].replace(",", "-").lower(),
                            react_dict,
                            entry_json["bib_record"],
                            en,
                            None,
                        )

                        write_to_exfortables_format_da(
                            entry_id,
                            dir,
                            filename,
                            entry_json["bib_record"],
                            react_dict,
                            mf + " - " + str(mt),
                            df2,
                        )

                    else:
                        ## case for ,DA with product
                        for prod in df2["residual"].unique():
                            df3 = df2[df2["residual"] == prod]
                            filename = exfortables_filename(
                                dir,
                                entry_id,
                                react_dict["process"].replace(",", "-").lower(),
                                react_dict,
                                entry_json["bib_record"],
                                en,
                                prod,
                            )

                            write_to_exfortables_format_da(
                                entry_id,
                                dir,
                                filename,
                                entry_json["bib_record"],
                                react_dict,
                                mf + " - " + str(mt),
                                df3,
                            )

            elif (
                react_dict["sf5"] == "PAR"
                and react_dict["process"].split(",")[1] == "INL"
            ):
                ## case for PAR,DA
                df = process_general(entry_id, entry_json, data_dict_conv)
                if df["en_inc"].isnull().values.all():
                    continue
                mf = get_mf(react_dict)

                for level_num in df["level_num"].unique():
                    df2 = df[df["level_num"] == level_num]
                    mt = df2["mt"].unique()

                    if not level_num:
                        level_num = 0
                        mt = "99"

                    dir = get_dir_name(react_dict, level_num=level_num, subdir=None)
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower()
                        + "-L"
                        + str(level_num),
                        react_dict,
                        entry_json["bib_record"],
                        None,
                        (
                            react_dict["target"].split("-")[1].capitalize()
                            + react_dict["target"].split("-")[2]
                            if len(react_dict["target"].split("-")) == 3
                            else react_dict["target"].split("-")[1].capitalize()
                            + react_dict["target"].split("-")[2]
                            + react_dict["target"].split("-")[3].lower()
                        ),
                    )

                    write_to_exfortables_format_da(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df2,
                    )

        ## ------------------------  Case for the angular distributions ------------------------  ##
        elif react_dict["sf6"] == "DE":
            if (
                not any(
                    par == react_dict["process"].split(",")[1]
                    for par in sf3_dict.keys()
                )
                or any(
                    react_dict["sf8"] != excep for excep in ("EXP") if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            df = process_general(entry_id, entry_json, data_dict_conv)
            if df["en_inc"].isnull().values.all():
                continue
            mf = get_mf(react_dict)
            mt = get_mt(react_dict)
            dir = get_dir_name(react_dict, level_num=None, subdir=None)

            for en in df["en_inc"].unique():
                df2 = df[df["en_inc"] == en]

                if (
                    react_dict["target"].split("-")[2] == "0"
                    and react_dict["sf4"] is None
                ):
                    ## case for ,DE without product such as (40-ZR-0(N,G),,DE)
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower(),
                        react_dict,
                        entry_json["bib_record"],
                        en,
                        None,
                    )

                    write_to_exfortables_format_de(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df2,
                    )

                else:
                    ## case for ,DA with product
                    for prod in df2["residual"].unique():
                        df3 = df2[df2["residual"] == prod]
                        filename = exfortables_filename(
                            dir,
                            entry_id,
                            react_dict["process"].replace(",", "-").lower(),
                            react_dict,
                            entry_json["bib_record"],
                            en,
                            prod,
                        )

                        write_to_exfortables_format_de(
                            entry_id,
                            dir,
                            filename,
                            entry_json["bib_record"],
                            react_dict,
                            mf + " - " + str(mt),
                            df3,
                        )

        ## ------------------------  Case for the fission neutrons ------------------------  ##
        elif react_dict["sf6"] == "NU":
            if (
                any(
                    excep in react_dict["sf8"]
                    for excep in ["MSC", "REL", "FRC", "RES", "RAW"]
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            df = process_general(entry_id, entry_json, data_dict_conv)
            if df["en_inc"].isnull().values.all():
                continue
            mf = get_mf(react_dict)
            mt = mt_nu_sf5[react_dict["sf5"]] if react_dict["sf5"] else "452"
            dir = get_dir_name(react_dict, level_num=None, subdir=mt)

            if react_dict["sf4"] is None:
                ## no reaction product would be given in these cases
                filename = exfortables_filename(
                    dir,
                    entry_id,
                    react_dict["process"].replace(",", "-").lower(),
                    react_dict,
                    entry_json["bib_record"],
                    None,
                    None,
                )

                write_to_exfortables_format_nu(
                    entry_id,
                    dir,
                    filename,
                    entry_json["bib_record"],
                    react_dict,
                    mf + " - " + str(mt),
                    df,
                )

            else:
                prod = react_dict["sf4"]  ## expect MASS, then format should be like FPY
                filename = exfortables_filename(
                    dir,
                    entry_id,
                    react_dict["process"].replace(",", "-").lower(),
                    react_dict,
                    entry_json["bib_record"],
                    None,
                    prod,
                )

                write_to_exfortables_format_fy(
                    entry_id,
                    dir,
                    filename,
                    entry_json["bib_record"],
                    react_dict,
                    mf + " - " + str(mt),
                    df,
                )

        elif (
            react_dict["sf6"] == "NU/DE" or react_dict["sf6"] == "FY/DE"
        ) and react_dict["sf5"] == "PR":
            # Prompt neutron/gamma spectra
            if (
                any(
                    excep in react_dict["sf8"]
                    for excep in ["MSC", "REL", "FRC", "RES", "RAW", "NPD"]  # MXD is ok
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            df = process_general(entry_id, entry_json, data_dict_conv)
            if df["en_inc"].isnull().values.all():
                continue
            mf = get_mf(react_dict)
            mt = get_mt(react_dict)
            dir = get_dir_name(react_dict, level_num=None, subdir=None)

            if react_dict["sf4"] is None and "NU" in react_dict["sf6"]:
                prod = "0-NN-1"
                for en in df["en_inc"].unique():
                    df2 = df[df["en_inc"] == en]
                    ## no reaction product would be given in these cases
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower(),
                        react_dict,
                        entry_json["bib_record"],
                        en,
                        prod,
                    )
                    write_to_exfortables_format_de(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df,
                    )

            else:
                for prod in df["residual"].unique():
                    df2 = df[df["residual"] == prod]
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower(),
                        react_dict,
                        entry_json["bib_record"],
                        None,
                        prod,
                    )

                    write_to_exfortables_format_de(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df2,
                    )

        ## ------------------------  Case for Kinetic Energy (KE or AKE) ------------------------  ##
        elif react_dict["sf6"] == "KE":
            if (
                any(
                    excep in react_dict["sf8"]
                    for excep in ["MSC", "REL", "FRC", "RES", "RAW"]
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            df = process_general(entry_id, entry_json, data_dict_conv)
            if df["en_inc"].isnull().values.all():
                continue
            mf = get_mf(react_dict)
            mt = mt_nu_sf5[react_dict["sf5"]] if react_dict["sf5"] else "452"
            dir = get_dir_name(react_dict, level_num=None, subdir=None)

            for en in df["en_inc"].unique():
                df2 = df[df["en_inc"] == en]
                if react_dict["sf4"] is None:
                    filename = exfortables_filename(
                        dir,
                        entry_id,
                        react_dict["process"].replace(",", "-").lower(),
                        react_dict,
                        entry_json["bib_record"],
                        en,
                        None,
                    )
                    write_to_exfortables_format_kinetic_e(
                        entry_id,
                        dir,
                        filename,
                        entry_json["bib_record"],
                        react_dict,
                        mf + " - " + str(mt),
                        df,
                    )

                else:
                    for prod in df["residual"].unique():
                        df3 = df2[df2["residual"] == prod]
                        filename = exfortables_filename(
                            dir,
                            entry_id,
                            react_dict["process"].replace(",", "-").lower(),
                            react_dict,
                            entry_json["bib_record"],
                            en,
                            prod,
                        )
                        write_to_exfortables_format_kinetic_e(
                            entry_id,
                            dir,
                            filename,
                            entry_json["bib_record"],
                            react_dict,
                            mf + " - " + str(mt),
                            df3,
                        )

        elif react_dict["sf6"] == "AKE":
            df = process_general(entry_id, entry_json, data_dict_conv)
            if df["en_inc"].isnull().values.all():
                continue
            mf = get_mf(react_dict)
            mt = sf3_dict[react_dict["process"].split(",")[1]]["mt"]
            dir = get_dir_name(react_dict, level_num=None, subdir=None)
            prod = react_dict["sf7"]

            for en in df["en_inc"].unique():
                df2 = df[df["en_inc"] == en]
                filename = exfortables_filename(
                    dir,
                    entry_id,
                    react_dict["process"].replace(",", "-").lower(),
                    react_dict,
                    entry_json["bib_record"],
                    en,
                    prod,
                )
                write_to_exfortables_format_kinetic_e(
                    entry_id,
                    dir,
                    filename,
                    entry_json["bib_record"],
                    react_dict,
                    mf + " - " + str(mt),
                    df2,
                )


        ## ------------------------  Case for the fission product yields ------------------------  ##
        elif react_dict["sf6"] == "FY":
            if (
                not any(par == react_dict["sf5"] for par in mt_fy.keys())
                or any(
                    excep in react_dict["sf8"]
                    for excep in ("MSC", "REL", "FRC", "RES", "RAW")
                    if react_dict["sf8"]
                )
                or react_dict["sf7"]
            ):
                continue

            df = process_general(entry_id, entry_json, data_dict_conv)
            if df["en_inc"].isnull().values.all():
                continue
            mf = get_mf(react_dict)
            mt = mt_fy[react_dict["sf5"]]
            dir = get_dir_name(react_dict, level_num=None, subdir=mt)

            for en in df["en_inc"].unique():
                df2 = df[df["en_inc"] == en]
                filename = exfortables_filename(
                    dir,
                    entry_id,
                    react_dict["process"].replace(",", "-").lower(),
                    react_dict,
                    entry_json["bib_record"],
                    en,
                    None,
                )
                write_to_exfortables_format_fy(
                    entry_id,
                    dir,
                    filename,
                    entry_json["bib_record"],
                    react_dict,
                    mf + " - " + str(mt),
                    df2,
                )

        ## ------------------------  Any other reactions which so far cannot be tabulated ------------------------  ##
        else:
            ### Generate reaction record for the cases if it is not possible to generate the tabulated data
            if react_dict:
                reac_data = [
                    {
                        "entry_id": entry_id,
                        "entry": entnum,
                        "target": react_dict["target"],
                        "projectile": react_dict["process"].split(",")[0],
                        "process": react_dict["process"],
                        "sf4": react_dict["sf4"],
                        "product_levels": None,
                        "e_inc_min": None,
                        "e_inc_max": None,
                        "points": None,
                        "sf5": react_dict["sf5"],
                        "sf6": react_dict["sf6"],
                        "sf7": react_dict["sf7"],
                        "sf8": react_dict["sf8"],
                        "sf9": react_dict["sf9"],
                        "x4_code": entry_json["reactions"][subent][pointer]["x4_code"],
                    }
                ]
                insert_reaction(reac_data)

    return


def main():
    ent = list_entries_from_df()
    entries = random.sample(ent, len(ent))

    drop_tables()
    del_outputs(OUT_PATH + "exfortables/")

    start_time = print_time()
    logging.info(f"Start processing {start_time}")

    for entnum in entries:
        if entnum.startswith("V"):
            continue
        print(entnum)

        entry_json = convert_exfor_to_json(entnum)
        write_dict_to_json(entnum, entry_json)

        try:
            if entry_json:
                bib_data = [
                    {
                        "entry": entry_json["entry"],
                        "title": entry_json["bib_record"]["title"]
                        if entry_json["bib_record"].get("title")
                        else None,
                        "first_author": entry_json["bib_record"]["authors"][0]["name"]
                        if entry_json["bib_record"].get("authors")
                        else None,
                        "authors": "".join(
                            [
                                entry_json["bib_record"]["authors"][i]["name"]
                                if entry_json["bib_record"].get("authors")
                                else None
                                for i in range(len(entry_json["bib_record"]["authors"]))
                            ]
                        ),
                        "first_author_institute": entry_json["bib_record"][
                            "institutes"
                        ][0]["x4_code"]
                        if entry_json["bib_record"].get("institutes")
                        else None,
                        "main_facility_institute": entry_json["bib_record"][
                            "facilities"
                        ][0]["institute"]
                        if entry_json["bib_record"].get("facilities")
                        else None,
                        "main_facility_type": entry_json["bib_record"]["facilities"][0][
                            "facility_type"
                        ]
                        if entry_json["bib_record"].get("facilities")
                        else None,
                        "main_reference": entry_json["bib_record"]["references"][0][
                            "x4_code"
                        ]
                        if entry_json["bib_record"].get("references")
                        else None,
                        "year": entry_json["bib_record"]["references"][0][
                            "publication_year"
                        ]
                        if entry_json["bib_record"].get("references")
                        else None,
                    }
                ]
                insert_bib(bib_data)
        except:
            pass

        if not entry_json.get("reactions"):
            continue

        common_main_dict = {}
        data_tables_dict = entry_json["data_tables"]
        data_dict = {}

        ## get SUBENT 001 COMMON block
        if data_tables_dict["001"].get("common"):
            common_main_dict = data_tables_dict["001"]["common"]

        ## looping over SUBENTRYs from 002
        for subent in list(data_tables_dict.keys())[1:]:
            # print(entnum, subent)
            common_sub_dict = {}

            ## get SUBENT 002 COMMON block
            if data_tables_dict[subent].get("common"):
                common_sub_dict = entry_json["data_tables"][subent]["common"]

            ## get SUBENT 002 DATA block
            if data_tables_dict[subent].get("data"):
                data_dict = dict_merge(
                    [
                        common_main_dict,
                        common_sub_dict,
                        entry_json["data_tables"][subent]["data"],
                    ]
                )

                ## Unify units
                data_dict_conv = unify_units(data_dict)

                ## Unify data length
                data_dict_conv = data_length_unify(data_dict)
                # print(data_dict_conv["heads"])

            else:
                ## means there is NODATA defined in the Subent
                continue

            entry_id = entnum + subent

            try:
                tabulated_to_exfortables_format(entry_id, entry_json, data_dict_conv)

            except:
                logging.error(f"ERROR: at ENTRY: '{entry_id}',")

    logging.info(f"End processing {print_time(start_time)}")


if __name__ == "__main__":
    main()
