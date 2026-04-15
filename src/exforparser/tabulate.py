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
import math
import pandas as pd
import logging
import random

from exforparser.json_converter import convert_exfor_to_json, write_dict_to_json
from exforparser.submodules.utilities.util import (
    dict_merge,
    print_time,
    print_process_time,
)
from exforparser.parser.list_x4files import (
    list_exfor_files,
    list_entries_from_pickle,
)
from exforparser.parser.exfor_unit import unify_units
from exforparser.parser.exfor_field import (
    ref_identifiers,
    experimental_condition_identifires,
)
from exforparser.parser.exfor_bib import correct_pub_year


import json
import numpy as np

from exforparser.tabulator.data_process import (
    data_length_unify,
    process_general,
    get_unique_mf_mt,
    process_cross_section_case,
    process_partial_cross_section_case,
    process_angular_distribution_section_case,
    process_partial_angular_distribution_case,
    process_energy_distribution_case,
    process_neutron_observables_case,
    process_misc_neutron_observables_case,
    process_fission_yield_case,
    process_thick_target_yield_case,
)
from exforparser.tabulator.data_filter import (
    filter_complex_reactions,
    filter_reaction,
    filter_cross_section_case,
    filter_partial_cross_section_case,
    filter_angular_distribution_case,
    filter_partial_angular_distribution_case,
    filter_energy_distribution_case,
    filter_misc_neutron_observables_case,
    filter_fission_yield_case,
)
from exforparser.sql.stored_insert import (
    insert_bib,
    insert_reaction,
    insert_reference,
    insert_reaction_index,
    insert_experimental_info,
    insert_native_data,
)


######## Creations of database records ###########
def create_and_insert_bib_dict(entnum, bib_record):
    bib_data = {
        "entry": entnum,
        "title": (bib_record["title"] if bib_record.get("title") else None),
        "first_author": (
            bib_record["authors"][0]["name"] if bib_record.get("authors") else None
        ),
        "authors": (
            ", ".join(a["name"] for a in bib_record["authors"])
            if bib_record.get("authors")
            else None
        ),
        "first_author_institute": (
            bib_record["institutes"][0]["x4_code"]
            if bib_record.get("institutes")
            else None
        ),
        "main_facility_institute": (
            bib_record["facilities"][0]["institute"]
            if bib_record.get("facilities")
            else None
        ),
        "main_facility_type": (
            bib_record["facilities"][0]["facility_type"]
            if bib_record.get("facilities")
            else None
        ),
        "main_reference": (
            bib_record["references"][0]["x4_code"]
            if bib_record.get("references")
            else None
        ),
        "main_doi": (
            bib_record["references"][0]["doi"] if bib_record.get("references") else None
        ),
        "doi_source": (
            "EXFOR"
            if bib_record.get("references") and bib_record["references"][0]["doi"]
            else None
        ),
        "year": (
            bib_record["references"][0]["publication_year"]
            if bib_record.get("references")
            else None
        ),
    }

    insert_bib(bib_data)

    return bib_data


def create_and_insert_references_dict(entry_id, partial_json):
    ref_data = []
    entry = entry_id[:5]

    if partial_json.get("references"):
        for ref in partial_json["references"]:
            ref_data += [
                {
                    "entry_id": entry_id,
                    "entry": entry,
                    "x4_code": ref["x4_code"],
                    "free_txt": " ".join(ref["free_txt"]),
                    "year": ref["publication_year"],
                    "doi": ref["doi"],
                    "type": "REFERENCE",
                }
            ]
    for reftype in ref_identifiers:
        if partial_json.get(reftype.lower()):
            for ref in partial_json[reftype.lower()]:
                ref_data += [
                    {
                        "entry_id": entry_id,
                        "entry": entry,
                        "x4_code": ref["x4_code"],
                        "free_txt": " ".join(ref["free_txt"]),
                        "year": (
                            correct_pub_year(ref["x4_code"]) if ref["x4_code"] else None
                        ),
                        "doi": None,
                        "type": reftype,
                    }
                ]
    if ref_data:
        insert_reference(ref_data)

    return


def create_and_insert_experimental_condition_dict(entry_id, exp_cond):
    exps_data = []

    for ec in experimental_condition_identifires:
        if exp_cond.get(ec.lower()):
            for e in exp_cond[ec.lower()]:
                exps_data += [
                    {
                        "entry_id": entry_id,
                        "x4_code": e["x4_code"],
                        "free_txt": " ".join(e["free_txt"]),
                        "type": ec,
                    }
                ]

    insert_experimental_info(exps_data)

    return


def create_and_insert_reaction_dict(entry_id, reactions_dict):
    ## Insert data table into exfor_reactions
    entnum, _, _ = entry_id.split("-")
    react_dict = reactions_dict["children"][0]
    reac_data = [
        {
            "entry_id": entry_id,
            "entry": entnum,
            "target": react_dict["target"] if react_dict.get("target") else None,
            "projectile": (
                react_dict["process"].split(",")[0]
                if react_dict.get("process")
                else None
            ),
            "process": react_dict["process"] if react_dict.get("process") else None,
            "sf4": react_dict["sf4"] if react_dict.get("sf4") else None,
            "sf5": react_dict["sf5"] if react_dict.get("sf5") else None,
            "sf6": react_dict["sf6"] if react_dict.get("sf6") else None,
            "sf7": react_dict["sf7"] if react_dict.get("sf7") else None,
            "sf8": react_dict["sf8"] if react_dict.get("sf8") else None,
            "sf9": react_dict["sf9"] if react_dict.get("sf9") else None,
            "x4_code": reactions_dict["x4_code"],
            "math_expression": str(reactions_dict["math_expression"]),
        }
    ]
    insert_reaction(reac_data)
    # print(reac_data)

    return react_dict


def safe_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _build_index_record(
    entry_id, entnum, react_dict, x4_code, residual, level_num, e_out,
    en_inc_min, en_inc_max, points, arbitrary_data, mf, mt,
    x_head=None, x_unit=None, y_head=None, y_unit=None,
):
    return {
        "entry_id": entry_id,
        "entry": entnum,
        "target": react_dict["target"],
        "projectile": react_dict["process"].split(",")[0],
        "process": react_dict["process"],
        "sf4": react_dict["sf4"],
        "residual": residual,
        "level_num": level_num,
        "e_out": e_out,
        "en_inc_min": en_inc_min,
        "en_inc_max": en_inc_max,
        "points": points,
        "arbitrary_data": arbitrary_data,
        "sf5": react_dict["sf5"],
        "sf6": react_dict["sf6"],
        "sf7": react_dict["sf7"],
        "sf8": react_dict["sf8"],
        "sf9": react_dict["sf9"],
        "x4_code": x4_code,
        "mf": None if mf is None or math.isnan(mf) else int(mf),
        "mt": safe_int(mt),
        "x_head": x_head,
        "x_unit": x_unit,
        "y_head": y_head,
        "y_unit": y_unit,
    }


def create_and_insert_reaction_index_dict(
    entry_id, entry_json, react_dict, df,
    x_head=None, x_unit=None, y_head=None, y_unit=None,
):
    entnum, subent, pointer = entry_id.split("-")
    x4_code = entry_json["reactions"][subent][pointer]["x4_code"]

    common = dict(x_head=x_head, x_unit=x_unit, y_head=y_head, y_unit=y_unit)

    if df.empty:
        insert_reaction_index([_build_index_record(
            entry_id, entnum, react_dict, x4_code,
            residual=react_dict["sf4"], level_num=None, e_out=None,
            en_inc_min=None, en_inc_max=None, points=None, arbitrary_data=None,
            mf=None, mt=None, **common,
        )])
        return None

    elif not df.loc[df["residual"].isnull() & df["level_num"].isnull()].empty:
        mf, mt = get_unique_mf_mt(df)
        insert_reaction_index([_build_index_record(
            entry_id, entnum, react_dict, x4_code,
            residual=None, level_num=None, e_out=None,
            en_inc_min=df["en_inc"].min(), en_inc_max=df["en_inc"].max(),
            points=len(df.index), arbitrary_data=df["arbitrary_data"].unique()[0],
            mf=mf, mt=mt, **common,
        )])

    else:
        for r in df["residual"].unique():
            for l in df["level_num"].unique():
                if pd.isna(l):
                    l = None
                    df2 = df[(df["residual"] == r) & (df["level_num"].isnull())]
                    for eo in df2["e_out"].unique():
                        mf, mt = get_unique_mf_mt(df2)
                        insert_reaction_index([_build_index_record(
                            entry_id, entnum, react_dict, x4_code,
                            residual=r, level_num=l, e_out=eo,
                            en_inc_min=df2["en_inc"].min(), en_inc_max=df2["en_inc"].max(),
                            points=len(df2.index), arbitrary_data=df2["arbitrary_data"].unique()[0],
                            mf=mf, mt=mt, **common,
                        )])
                    continue

                elif r and isinstance(l, np.integer):
                    df2 = df[(df["residual"] == r) & (df["level_num"] == l)]
                else:
                    df2 = df.copy()

                mf, mt = get_unique_mf_mt(df2)
                insert_reaction_index([_build_index_record(
                    entry_id, entnum, react_dict, x4_code,
                    residual=r, level_num=int(l) if isinstance(l, np.integer) else None,
                    e_out=df2["e_out"].unique()[0],
                    en_inc_min=df2["en_inc"].min(), en_inc_max=df2["en_inc"].max(),
                    points=len(df2.index), arbitrary_data=df2["arbitrary_data"].unique()[0],
                    mf=mf, mt=mt, **common,
                )])

        return df2


def create_and_insert_native_data_dict(entry_id, entry_num, subent, column_type, data_dict):
    for index, (head, unit, values) in enumerate(
        zip(data_dict["heads"], data_dict["units"], data_dict["data"])
    ):
        pointer = None
        if len(head) == 11:
            pointer = head[10]

        datadict = {
            "entry_id": entry_id,
            "entry": entry_num,
            "subent": subent,
            "column_index": index,
            "column_type": column_type,
            "pointer": pointer,
            "head": head,
            "unit": unit,
            "data": json.dumps(values),
        }
        insert_native_data(datadict)

    return


######## Main Process ###########


def process(entnum):
    entry_json = convert_exfor_to_json(entnum)

    if entry_json:
        ## Dump JSON into a file
        write_dict_to_json(entnum, entry_json)

        ## create bib record in SQLite
        main_bib_dict = create_and_insert_bib_dict(entnum, entry_json["bib_record"])
        create_and_insert_references_dict(
            entnum + "-" + "001-0", entry_json["bib_record"]
        )

    common_main_dict = {}
    data_dict = {}

    ## Get SUBENT 001 COMMON block
    if entry_json["data_tables"]["001"].get("common"):
        common_main_dict = entry_json["data_tables"]["001"]["common"]
        ## register the common experimental conditions
        ## Store the original COMMON data in SQL
        """
        e.g. {
            'heads': ['MONIT-ERR', 'ERR-1', 'ERR-2', 'ERR-3', 'ERR-4', 'ERR-HL'], 
            'units': ['PER-CENT', 'PER-CENT', 'PER-CENT', 'PER-CENT', 'PER-CENT', 'HR'], 
            'data': [[2.0], [4.0], [2.0], [5.2], [0.5], [0.0012]]
        }
        """
        create_and_insert_native_data_dict(entnum + "-001-0", entnum, "001", "COMMON", common_main_dict)

    if entry_json["experimental_conditions"].get("001"):
        create_and_insert_experimental_condition_dict(
            entnum + "-" + "001-0", entry_json["experimental_conditions"]["001"]["0"]
        )
        create_and_insert_references_dict(
            entnum + "-" + "001-0", entry_json["experimental_conditions"]["001"]["0"]
        )

    ## Looping over SUBENTRYs from 002 to 999
    for subent in list(entry_json["data_tables"].keys())[1:]:
        common_sub_dict = {}
        entry_num = entnum + subent

        ## get SUBENT 002-999 COMMON block
        if entry_json["data_tables"][subent].get("common"):
            common_sub_dict = entry_json["data_tables"][subent]["common"]
            create_and_insert_native_data_dict(
                entnum + "-" + subent + "-0", entnum, subent, "COMMON", common_sub_dict
            )

        ## get SUBENT 002-999 DATA block
        if entry_json["data_tables"][subent].get("data"):
            ## Store original HEAD and UNIT in SQL
            create_and_insert_native_data_dict(
                entnum + "-" + subent + "-0", entnum, subent, "DATA", entry_json["data_tables"][subent]["data"]
            )

            data_dict = dict_merge(
                [
                    common_main_dict,
                    common_sub_dict,
                    entry_json["data_tables"][subent]["data"],
                ]
            )
            """
            {'heads': ['E-MIN', 'EN-MEAN', 'EN-RSL-FW', 'DATA', 'DATA-ERR'], 
            'units': ['MEV', 'KEV', 'KEV', 'PRT/REAC', 'PRT/REAC'], 
            'data': [[0.6], [48.0, 550.0], [None, 170.0], [2.26, 2.27], [0.09, 0.21]]}
            """

            ## Unify data length
            data_dict_conv = data_length_unify(data_dict)

            ## Unify units, convert e.g. MeV to eV
            data_dict_conv = unify_units(data_dict_conv)

        else:
            ## means there is NODATA defined in the Subent
            continue

        ## Process all pointers
        process_pointers(entry_num, main_bib_dict, entry_json, data_dict_conv)

    return


def process_all():
    ent = []
    # df = list_exfor_files()
    df = list_entries_from_pickle()
    # insert_history(df)

    for _, row in df.iterrows():
        ent += [row["entry"]]
    entries = random.sample(ent, len(ent))

    start_time = print_process_time()
    logging.info(f"Start processing {print_time()}")

    for entnum in entries:
        print(entnum)
        # process(entnum)
        try:
            process(entnum)
        except KeyboardInterrupt:
            print("CTR + C")
            break
        except Exception:
            logging.error(f"ERROR: at ENTRY: {entnum}", exc_info=True)

    logging.info(f"End processing {print_process_time(start_time)}")


def process_updated_entry():
    ent = []
    old_df = list_entries_from_pickle()
    new_df = list_exfor_files()

    if old_df.equals(new_df):
        return

    # addtion, update
    df_diff = old_df.compare(new_df)

    for _, row in df_diff.iterrows():
        ent += [row["entry"]]

    entries = ent

    start_time = print_process_time()
    logging.info(f"Start processing {print_time()}")

    for entnum in entries:
        print(entnum)
        # process(entnum)
        try:
            process(entnum)
        except KeyboardInterrupt:
            print("CTR + C")
            break
        except Exception:
            logging.error(f"ERROR: at ENTRY: {entnum}", exc_info=True)

    logging.info(f"End processing {print_process_time(start_time)}")


def process_pointers(entry_num, main_bib_dict, entry_json, data_dict_conv):
    entnum = entry_num[0:5]
    subent = entry_num[5:8]
    print(entnum, subent)
    logging.info(f"Process {entnum}-{subent}")

    for pointer in entry_json["reactions"][subent]:
        ## looping over all pointers exist in the REACTION in SUBENTRY
        df = pd.DataFrame()
        entry_id = entnum + "-" + subent + "-" + pointer

        ## Insert REACTION code for each pointer into the exfor_reactions table
        create_and_insert_reaction_dict(
            entry_id, entry_json["reactions"][subent][pointer]
        )

        if entry_json["experimental_conditions"][subent].get(pointer):
            create_and_insert_experimental_condition_dict(
                entry_id, entry_json["experimental_conditions"][subent][pointer]
            )
            create_and_insert_references_dict(
                entry_id, entry_json["experimental_conditions"][subent][pointer]
            )

        if filter_complex_reactions(entry_json, subent, pointer):
            continue

        react_dict = entry_json["reactions"][subent][pointer]["children"][0]

        ## Store datatable into SQL; also returns axis head/unit metadata
        df, x_head, x_unit, y_head, y_unit = process_general(entry_id, entry_json, data_dict_conv)

        ## Insert EXFOR reaction index into the exfor_index table
        create_and_insert_reaction_index_dict(
            entry_id, entry_json, react_dict, df,
            x_head=x_head, x_unit=x_unit, y_head=y_head, y_unit=y_unit,
        )

        tabulate_into_exfortables_format(entry_id, main_bib_dict, react_dict, df)

    return


def tabulate_into_exfortables_format(entry_id, main_bib_dict, react_dict, df):

    if filter_reaction(react_dict, df):
        ## Filter some major cases that cannot be processed as a tablated format,
        ## such as the cases that DATA is given by arbitrary unit (ARB-UNIT) or no dimension (NO-DIM)
        return
    if react_dict["sf6"] == "SIG":
        if filter_cross_section_case(react_dict, df):
            return

        if react_dict["sf5"] != "PAR":
            process_cross_section_case(df, entry_id, main_bib_dict, react_dict)
        else:
            ## none of (N,NON) PAR,SIG are useful
            if filter_partial_cross_section_case(react_dict, df):
                return
            process_partial_cross_section_case(df, entry_id, main_bib_dict, react_dict)

    # --------------------------------------------------------------------------------------- ##
    # ------------------------        Angular distributions         ------------------------  ##
    # --------------------------------------------------------------------------------------- ##

    elif react_dict["sf6"] == "DA":
        if filter_angular_distribution_case(react_dict, df):
            return

        if react_dict["sf5"] != "PAR":
            process_angular_distribution_section_case(
                df, entry_id, main_bib_dict, react_dict
            )

        elif (
            react_dict["sf5"] == "PAR" and react_dict["process"].split(",")[1] == "INL"
        ):
            if filter_partial_angular_distribution_case(react_dict, df):
                return
            process_partial_angular_distribution_case(
                df, entry_id, main_bib_dict, react_dict
            )

    # --------------------------------------------------------------------------------------- ##
    # ------------------------         Energy distributions         ------------------------  ##
    # --------------------------------------------------------------------------------------- ##

    elif react_dict["sf6"] == "DE":
        if filter_energy_distribution_case(react_dict, df):
            return
        process_energy_distribution_case(df, entry_id, main_bib_dict, react_dict)

    # --------------------------------------------------------------------------------------- ##
    # ------------------------         Neutron observables          ------------------------  ##
    # --------------------------------------------------------------------------------------- ##
    elif react_dict["sf6"] == "NU":
        if (
            not (react_dict["sf6"] == "NU/DE" or react_dict["sf6"] == "FY/DE")
            and react_dict["sf5"] == "PR"
        ):

            if filter_misc_neutron_observables_case(react_dict, df):
                return
            process_neutron_observables_case(df, entry_id, main_bib_dict, react_dict)

        else:
            if filter_misc_neutron_observables_case(react_dict, df):
                return
            process_misc_neutron_observables_case(
                df, entry_id, main_bib_dict, react_dict
            )

    ## --------------------------------------------------------------------------------------- ##
    ## ------------------------           Kinetic energies           ------------------------  ##
    ## --------------------------------------------------------------------------------------- ##

    # --------------------------------------------------------------------------------------- ##
    # ------------------------            Fission yields            ------------------------  ##
    # --------------------------------------------------------------------------------------- ##
    elif react_dict["sf6"] == "FY":
        if filter_fission_yield_case(react_dict, df):
            return
        process_fission_yield_case(df, entry_id, main_bib_dict, react_dict)

    # --------------------------------------------------------------------------------------- ##
    # ------------------------            Target yields             ------------------------  ##
    # --------------------------------------------------------------------------------------- ##
    elif react_dict["sf6"] == "TTY":
        if filter_fission_yield_case(react_dict, df):
            return
        process_thick_target_yield_case(df, entry_id, main_bib_dict, react_dict)

    ## --------------------------------------------------------------------------------------- ##
    ## ------------------------         Resonance parameters         ------------------------  ##
    ## --------------------------------------------------------------------------------------- ##


if __name__ == "__main__":
    process_all()
