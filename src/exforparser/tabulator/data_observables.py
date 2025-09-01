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
###################################################################
import pandas as pd
import numpy as np
import re
from collections import defaultdict

from exforparser.sql.stored import (
    list_of_target,
    list_of_reactions_and_entries,
    observable_data_query,
    resonance_parameter_query,
    data_query_by_id,
)
from exforparser.submodules.utilities.util import del_outputs, closest, slices
from exforparser.submodules.utilities.reaction import sf3_dict, sig_sf5

from .data_dir_files import (
    get_thermal_dir_name,
    get_thermal_filename,
    get_resonance_param_dir_name,
    get_resonance_param_file_name,
)
from .data_write import (
    write_to_thermal_table,
    write_to_resonance_spacing_table,
    write_to_exfortables_format_resonance_parameter,
)
from .data_filter import filter_cross_section_case, filter_partial_cross_section_case
from .data_process import process_cross_section_case, process_partial_cross_section_case
import logging

pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.width", 2000, "max_colwidth", None)


def crosssection():
    type = "xs"

    target_dict = list_of_reactions_and_entries(type)
    """
    return example:
    target_dict = {
        ....
        '95-AM-244-M': {'N,F': ['14047-005-0']}, 
        '96-CM-240': {'N,F': ['14229-014-0']}, 
        '96-CM-241': {'N,F': ['14229-015-0']}, 
        '96-CM-242': {'N,F': ['40597-002-0', '23076-004-0', '14229-016-0', '12496-008-0', '12991-002-0', '20881-019-0', '40779-007-0'], 
                    'N,G': ['22941-005-0', '22941-017-0', '22941-018-0', '20881-018-0']},
        }
    """
    # print(target_dict)
    # target_dict = {'1-H-D2O': {'N,G': ['20460-003-0']} }
    # target_dict = {"13-AL-27": {"N,INL": ['41323-009-0']}}
    # target_dict = {"12-MG-24": {"N,G": ['13544-002-0']}}
    # target_dict = {"6-C-12": {"N,A": ['14711-002-0']}}

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            # print(target, reaction, entries)
            for ent in entries:
                print(target, reaction, ent)
                entry_json = {}
                df = data_query_by_id(type, [ent])
                # print(df)
                if df.empty:
                    continue

                react_dict = df.iloc[0].to_dict()

                if filter_cross_section_case(react_dict, df):
                    continue

                entry_json["bib_record"] = {
                    "first_author": react_dict["first_author"].split(".")[-1],
                    "year": react_dict["year"],
                    "first_author_institute": react_dict["first_author_institute"],
                    "main_facility_institute": react_dict["main_facility_institute"],
                    "main_facility_type": react_dict["main_facility_type"],
                    "main_reference": react_dict["main_reference"],
                }
                # print(df)
                try:
                    if react_dict["sf5"] is None or any(
                        sf5 == react_dict["sf5"] for sf5 in sig_sf5.keys()
                    ):
                        process_cross_section_case(
                            df, react_dict["entry_id"], entry_json, react_dict
                        )

                    if react_dict["sf5"] == "PAR":
                        ## none of (N,NON) PAR,SIG are useful
                        if filter_partial_cross_section_case(react_dict, df):
                            continue
                        process_partial_cross_section_case(
                            df, react_dict["entry_id"], entry_json, react_dict
                        )

                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except:
                    logging.error(f"ERROR: at {target_dict}", exc_info=True)


def thermal(type):
    thermal_data_reaction = ["N,TOT", "N,G", "N,P", "N,A", "N,EL", "N,F"]
    targets = list_of_target(type)

    # del_outputs(os.path.join(OUT_PATH, "thermaldata"))

    for target in targets:
        for reaction in thermal_data_reaction:
            # df = thermal_xs(target, reaction)
            df = observable_data_query(type, target, reaction)
            # print(df.sort_values(by="sf4"))
            for prod in df["sf4"].unique():
                react_dict = {"target": target, "process": reaction, "sf4": prod}

                if prod is None:
                    df2 = df[df["sf4"].isnull()]

                else:
                    df2 = df[df["sf4"] == prod]

                if df2.empty:
                    continue

                else:
                    if type == "thermal":
                        dir = get_thermal_dir_name("thermaldata/thermal_xs", react_dict)
                        outfile = get_thermal_filename(dir, react_dict)

                        write_to_thermal_table(type, dir, outfile, react_dict, df2)
    return


def read_ripl3_d0():
    # Z = El = A = Io = Bn = D0 = dD = S0 = dS = Gg = dG = Com = []
    path = "/Users/okumuras/Dropbox/Development/exforparser/examples/resonances_0.ripl3"
    df = pd.read_fwf(
        path,
        sep="\s+",
        comment="#",
        names=["Z", "El", "A", "Io", "Bn", "D0", "dD", "S0", "dS", "Gg", "dG", "Com."],
        dtype={"Gg": np.float64, "dG": np.float64},
        colspecs="infer",
    )
    return df


def read_ripl3_d1():
    path = "/Users/okumuras/Dropbox/Development/exforparser/examples/resonances_1.ripl3"
    df = pd.read_fwf(
        path,
        sep="\s+",
        comment="#",
        names=["Z", "El", "A", "Io", "Bn", "D1", "dD", "S1", "dS", "Gg", "dG", "Com."],
        dtype={"Gg": np.float64, "dG": np.float64},
        colspecs="infer",
    )
    return df


def resonance_spacing():
    """
    To extract the resonance spacing (N,0),,D reactions for Arjan Koning
    """
    type = "resonance_spacing"
    targets = list_of_target(type)

    ripl_d0 = read_ripl3_d0()
    ripl_d1 = read_ripl3_d1()

    for target in targets:
        reactions = ["N,0", "N,EL"]
        for reaction in reactions:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            z = target.split("-")[0]
            el = target.split("-")[1].title()
            a = target.split("-")[2]
            # print(z, el, a)
            df0 = ripl_d0[
                (ripl_d0["Z"] == int(z))
                & (ripl_d0["El"] == el)
                & (ripl_d0["A"] == int(a))
            ]
            df1 = ripl_d1[
                (ripl_d1["Z"] == int(z))
                & (ripl_d1["El"] == el)
                & (ripl_d1["A"] == int(a))
            ]

            dir = get_thermal_dir_name("resonance_data/resonance_spacing", react_dict)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_resonance_spacing_table(
                type, dir, outfile, react_dict, df, df0, df1
            )

    return


def resonance_integral():
    """
    To extract the resonance integral data, (N,G),,RI
    """
    reactions = ["N,TOT", "N,G", "N,P", "N,A", "N,ABS", "N,F", "N,SCT"]
    type = "resonance_integral"
    targets = list_of_target(type)

    for target in targets:
        for reaction in reactions:
            df = pd.DataFrame()
            print(target, reaction)
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            dir = get_thermal_dir_name("resonance_data/resonance_integral", react_dict)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_thermal_table(type, dir, outfile, react_dict, df)

    return


def macs():
    """
    To extract the Maxwellian average cross section, (N,x),,SIG,,MXW
    """
    reactions = ["N,G"]
    type = "macs"
    targets = list_of_target(type)
    for target in targets:
        for reaction in reactions:
            df = pd.DataFrame()
            print(target, reaction)
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            for i, row in df.groupby(["entry_id"], group_keys=False):

                if len(row) > 1:
                    ## if there are more than one incident energy close to 30 keV, select one of the closest
                    one_en = closest(row["en_inc"].unique(), 0.03)
                    df = df.drop(
                        df[(df["entry_id"] == i[0]) & (df["en_inc"] != one_en)].index
                    )

            dir = get_thermal_dir_name("resonance_data/macs", react_dict)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_thermal_table(type, dir, outfile, react_dict, df)

    return


def resonance_parameter():
    """
    Extract resonance parameter data grouped by ENTRY-SUBENT,
    combining multiple reactions horizontally.
    """

    projectiles = ["P", "A", "G", "N"]
    obs_type = "resonance_parameter"
    rp_sf6 = ["WID", "WID/STR", "WID/RED", "ARE", "RMT", "RMT/AMP"]

    targets = list_of_target(obs_type)

    # targets = ["9-F-19"]
    for target in reversed(targets):
        for projectile in projectiles:

            fixed_columns = [
                "en_inc",
                "den_inc",
                f"data({projectile},TOT)",
                f"ddata({projectile},TOT)",
                f"data({projectile},G)",
                f"ddata({projectile},G)",
                f"data({projectile},EL)",
                f"ddata({projectile},EL)",
                f"data({projectile},F)",
                f"ddata({projectile},F)",
                f"data({projectile},A)",
                f"ddata({projectile},A)",
            ]

            for sf6 in rp_sf6:
                print(f"Projectile: {projectile} Target: {target} SF6:{sf6}")
                react_dict = {
                    "target": target,
                    "process": f"{projectile},0",
                    "sf4": None,
                }
                df = resonance_parameter_query(obs_type, sf6, target, f"{projectile},0")
                # print(df[["entry_id", "process", "en_inc", "den_inc", "data", "ddata", "en_inc_frame"]])
                if df.empty:
                    continue

                for entry_subent, row in df.groupby(
                    df["entry_id"].str[:9], group_keys=False
                ):
                    # print(entry_subent)
                    main_bib_dict = (
                        row[
                            [
                                "first_author",
                                "first_author_institute",
                                "main_facility_institute",
                                "main_facility_type",
                                "main_reference",
                                "year",
                            ]
                        ]
                        .iloc[0]
                        .to_dict()
                    )
                    main_bib_dict["authors"] = [{"name": main_bib_dict["first_author"]}]
                    main_bib_dict["entry_id"] = entry_subent

                    react_dict["entry_id"] = row["entry_id"].unique()[0]
                    react_dict["x4_code"] = row["x4_code"].unique()[0]
                    react_dict["sf6"] = sf6
                    react_dict["process"] = row["process"].unique()[0]
                    react_dict["en_res_type"] = row["en_res_type"].unique()[0]
                    # react_dict = row[["entry_id",
                    #                 "x4_code",
                    #                 "process",
                    #                 "residual",
                    #                 "sf4",
                    #                 "sf5",
                    #                 "sf6",
                    #                 "sf7",
                    #                 "sf8",
                    #                 "sf9"]].to_dict()
                    react_dict["target"] = target
                    react_dict["projectile"] = projectile
                    # print(row[["entry_id", "process", "en_inc", "den_inc", "data", "ddata", "width_str", "dwidth_str", "en_inc_frame"]])

                    pivot_df = row.pivot_table(
                        index=["en_inc"],
                        columns="process",
                        values=["data", "ddata"],
                        dropna=False,
                    )

                    ## Delete column if all data are Nan
                    # data_cols = pivot_df["data"]
                    # pivot_df = pivot_df[~data_cols.isna().all(axis=1)]

                    pivot_df.columns = [
                        f"{col[0]}({col[1]})" for col in pivot_df.columns
                    ]
                    pivot_df = pivot_df.reset_index()

                    den_map = row.drop_duplicates("en_inc")[["en_inc", "den_inc"]]
                    pivot_df["en_inc"] = pivot_df["en_inc"].astype(float)
                    den_map["en_inc"] = den_map["en_inc"].astype(float)
                    pivot_df = pivot_df.merge(den_map, on="en_inc", how="left")

                    for col in fixed_columns:
                        if col not in pivot_df.columns:
                            pivot_df[col] = np.nan

                    pivot_df = pivot_df[fixed_columns]
                    pivot_df = pivot_df.where(pd.notnull(pivot_df), np.nan)

                    ## C2972-007, There is no EN for the first data
                    pivot_df = pivot_df.dropna(subset=["en_inc"])

                    ## Add spin and momentum to the dataframe
                    extra_cols = row[
                        ["en_inc", "momentum_l", "spin_j"]
                    ].drop_duplicates(subset=["en_inc"])
                    extra_cols["en_inc"] = extra_cols["en_inc"].astype(float)

                    pivot_df = pivot_df.reset_index().merge(
                        extra_cols, on=["en_inc"], how="left"
                    )

                    if pivot_df.empty:
                        continue

                    dir = get_resonance_param_dir_name(
                        "resonance_data/resonance_parameter", sf6, react_dict
                    )
                    outfile = get_resonance_param_file_name(
                        dir, entry_subent, main_bib_dict, react_dict
                    )
                    write_to_exfortables_format_resonance_parameter(
                        entry_subent, dir, outfile, main_bib_dict, react_dict, pivot_df
                    )

    return


# def resonance_parameter():
#     """
#     Extract and combine resonance parameter data by SENTRY_ID (entry_id).
#     Write one file per entry_id combining all relevant reactions.
#     """
#     resonance_data_reaction = ["N,TOT", "N,G", "N,EL", "N,F", "N,A"]
#     type = "resonance_parameter"
#     targets = list_of_target(type)

#     for target in reversed(targets):
#         print(f"Processing target: {target}")

#         # 一時保存用 dict: entry_id → { 'en': df, 'channels': {channel: df} }
#         entry_data_dict = defaultdict(lambda: {"en_df": None, "channels": {}})

#         for reaction in resonance_data_reaction:
#             react_dict = {"target": target, "process": reaction, "sf4": None}
#             en_df, df = observable_data_query(type, target, reaction)

#             if df.empty:
#                 continue

#             # entry_id 単位にグループ化して格納
#             df["reaction"] = df["x4_code"].apply(lambda x: extract_reaction(x))
#             entry_ids = df["entry_id"].unique()

#             for entry_id in entry_ids:
#                 sub_df = df[df["entry_id"] == entry_id].copy()
#                 if sub_df.empty:
#                     continue

#                 # reaction typeごとの列を用意
#                 for ch in sub_df["reaction"].dropna().unique():
#                     ch_df = sub_df[sub_df["reaction"] == ch][["data", "ddata"]].reset_index(drop=True)
#                     entry_data_dict[entry_id]["channels"][ch] = ch_df

#                 # ENのデータも保存（1回だけ）
#                 if entry_data_dict[entry_id]["en_df"] is None and not en_df.empty:
#                     df_en_clean = en_df[["data", "ddata"]].copy()
#                     df_en_clean.columns = ["en", "d_en"]
#                     entry_data_dict[entry_id]["en_df"] = df_en_clean.reset_index(drop=True)

#         # 出力フェーズ：entry_id単位でファイルを作成
#         for entry_id, data in entry_data_dict.items():
#             if data["en_df"] is None:
#                 continue

#             output_df = data["en_df"].copy()

#             for ch, ch_df in data["channels"].items():
#                 ch_df.columns = [ch, f"d_{ch}"]
#                 output_df = pd.concat([output_df, ch_df], axis=1)

#             # 保存パス生成
#             react_dict["entry_id"] = entry_id
#             dir = get_thermal_dir_name("resonance_data/resonance_parameter", react_dict)
#             outfile = get_thermal_filename(dir, react_dict)

#             # 保存（必要であればコメントアウト解除）
#             # write_to_exfortables_format_resonance_parameter(type, dir, outfile, react_dict, output_df)

#             print(f"\n[{entry_id}]")
#             print(output_df)

#     return


# ユーティリティ関数（再掲）
def extract_reaction(x4_code):
    match = re.search(r"\(.*?\((N,[^)]+)\)", x4_code)
    return match.group(1).split(",")[1] if match else None


def gamma_gamma():
    """
    To extract the resonance spacing (N,0),,D reactions for Arjan Koning
    """
    resonance_data_reaction = ["N,G"]
    type = "gamma_gamma"
    targets = list_of_target(type)

    ripl_d0 = read_ripl3_d0()
    ripl_d1 = read_ripl3_d1()

    for target in targets:
        print(target)
        for reaction in resonance_data_reaction:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            z = target.split("-")[0]
            el = target.split("-")[1].title()
            a = target.split("-")[2]
            # print(z, el, a)
            df0 = ripl_d0[
                (ripl_d0["Z"] == int(z))
                & (ripl_d0["El"] == el)
                & (ripl_d0["A"] == int(a))
            ]
            df1 = ripl_d1[
                (ripl_d1["Z"] == int(z))
                & (ripl_d1["El"] == el)
                & (ripl_d1["A"] == int(a))
            ]
            df0 = df0.drop(df0[df0["Gg"].isnull()].index)
            df1 = df1.drop(df1[df1["Gg"].isnull()].index)

            dir = get_thermal_dir_name("resonance_data/gamma_gamma", react_dict)
            outfile = get_thermal_filename(dir, react_dict)
            write_to_resonance_spacing_table(
                type, dir, outfile, react_dict, df, df0, df1
            )

    return
    # write_to_resonance_spacing_table(dir, outfile, react_dict)
