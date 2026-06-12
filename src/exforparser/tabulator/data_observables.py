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

from exforparser.config import engines
from exforparser.sql.stored_query import (
    list_of_target,
    list_of_reactions_and_entries,
    observable_data_query,
    resonance_parameter_data_query,
    data_query_by_id,
)
from exforparser.submodules.utilities.util import del_outputs, closest, slices
from exforparser.submodules.utilities.reaction import sf3_dict, sig_sf5, resonance_parameter_sf6
from exforparser.submodules.utilities.elem import elemtoz_nz


from .data_dir_files import (
    get_obs_dir_name,
    get_reference_obs_dir_name,
    get_thermal_filename,
    get_resonance_param_dir_name,
    get_reference_resonance_param_dir_name,
    get_resonance_param_file_name,
)
from .data_write import (
    write_to_thermal_table,
    write_to_resonance_spacing_table,
    write_to_exfortables_format_resonance_parameter,
)
from .data_filter import (
    filter_cross_section_case,
    filter_partial_cross_section_case,
    filter_angular_distribution_case,
    filter_partial_angular_distribution_case,
    filter_energy_distribution_case,
    filter_double_differential_cross_section_case,
    filter_fission_yield_case,
    filter_misc_neutron_observables_case,
)
from .data_process import (
    process_cross_section_case,
    process_partial_cross_section_case,
    process_angular_distribution_section_case,
    process_partial_angular_distribution_case,
    process_energy_distribution_case,
    process_double_differential_cross_section_case,
    process_fission_yield_case,
    process_neutron_observables_case,
    process_misc_neutron_observables_case,
)
import logging

pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.width", 2000, "max_colwidth", None)


def _iter_entry_data(obs_type, entries, chunk_size=25):
    """Fetch one target/reaction entry batch, then yield per-entry dataframes."""
    for start in range(0, len(entries), chunk_size):
        chunk = entries[start:start + chunk_size]
        print(
            f"{obs_type}: loading entries {start + 1}-{start + len(chunk)}"
            f"/{len(entries)}",
            flush=True,
        )
        df_all = data_query_by_id(obs_type, chunk)
        if df_all.empty:
            continue

        grouped = {
            entry_id: df
            for entry_id, df in df_all.groupby("entry_id", sort=False)
        }
        for ent in chunk:
            df = grouped.get(ent)
            if df is not None and not df.empty:
                yield ent, df


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
            for ent, df in _iter_entry_data(type, entries):
                print("crosssection():", target, reaction, ent)

                react_dict = df.iloc[0].to_dict()

                if filter_cross_section_case(react_dict, df):
                    continue

                main_bib_dict = {
                    "first_author": react_dict["first_author"],
                    "year": react_dict["year"],
                    "first_author_institute": react_dict["first_author_institute"],
                    "main_facility_institute": react_dict["main_facility_institute"],
                    "main_facility_type": react_dict["main_facility_type"],
                    "main_reference": react_dict["main_reference"],
                }
                try:
                    if react_dict["sf5"] is None or any(
                        sf5 == react_dict["sf5"] for sf5 in sig_sf5.keys()
                    ):
                        process_cross_section_case(
                            df, react_dict["entry_id"], main_bib_dict, react_dict
                        )

                    if react_dict["sf5"] == "PAR":
                        if filter_partial_cross_section_case(react_dict, df):
                            continue
                        process_partial_cross_section_case(
                            df, react_dict["entry_id"], main_bib_dict, react_dict
                        )

                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except Exception:
                    logging.error(f"ERROR: at {ent}", exc_info=True)


def thermal(type):
    thermal_data_reaction = ["N,TOT", "N,G", "N,P", "N,A", "N,EL", "N,F"]
    targets = list_of_target(type)
    # targets = ["56-BA-130"]
    for target in targets:
        for reaction in thermal_data_reaction:
            print("thermal()", target, reaction)
            df = observable_data_query(type, target, reaction)
            for prod in df["sf4"].unique():
                react_dict = {"target": target, "process": reaction, "sf4": prod}

                if prod is None:
                    df2 = df[df["sf4"].isnull()]

                else:
                    df2 = df[df["sf4"] == prod]

                if df2.empty:
                    continue

                if df2["data"].isna().all():
                    ## This is for the case of #21992003
                    continue

                else:
                    if type == "thermal":
                        dir = get_reference_obs_dir_name("thermal", react_dict)
                        outfile = get_thermal_filename(dir, react_dict)

                        write_to_thermal_table(type, dir, outfile, react_dict, df2)
    return


def _split_endftables_target(target):
    match = re.match(r"^([A-Z][a-z]?)(\d+)", str(target))
    if not match:
        return pd.Series({"Z": np.nan, "El": None, "A": np.nan})
    el, mass = match.groups()
    z = elemtoz_nz(el)
    return pd.Series({"Z": int(z) if z else np.nan, "El": el, "A": int(mass)})


def _read_ripl3_from_endftables(level: int):
    spacing = f"D{level}"
    gamma = f"gamgam{level}"
    stmt = """
        SELECT
            r.target,
            r.obs_type,
            d.value,
            d.dvalue
        FROM endf_reactions AS r
        JOIN resonancetable_data AS d
          ON r.reaction_id = d.reaction_id
        WHERE r.evaluation = 'RIPL-3'
          AND r.obs_type IN (?, ?)
    """
    with engines["endftables"].connect() as conn:
        df = pd.read_sql(stmt, conn, params=(spacing, gamma))

    if df.empty:
        columns = ["Z", "El", "A", spacing, "dD", "Gg", "dG"]
        return pd.DataFrame(columns=columns)

    target_parts = df["target"].apply(_split_endftables_target)
    df = pd.concat([df, target_parts], axis=1)
    values = df.pivot_table(
        index=["Z", "El", "A"],
        columns="obs_type",
        values=["value", "dvalue"],
        aggfunc="first",
    ).reset_index()

    values.columns = [
        "_".join(str(part) for part in col if part) if isinstance(col, tuple) else col
        for col in values.columns
    ]
    values = values.rename(
        columns={
            f"value_{spacing}": spacing,
            f"dvalue_{spacing}": "dD",
            f"value_{gamma}": "Gg",
            f"dvalue_{gamma}": "dG",
        }
    )
    for column in (spacing, "dD", "Gg", "dG"):
        if column not in values:
            values[column] = np.nan
    return values[["Z", "El", "A", spacing, "dD", "Gg", "dG"]]


def read_ripl3_d0():
    return _read_ripl3_from_endftables(0)


def read_ripl3_d1():
    return _read_ripl3_from_endftables(1)


def _obs_output_dir(obs_type, react_dict, pure_exfor=False):
    if pure_exfor:
        return get_obs_dir_name(obs_type, react_dict)
    return get_reference_obs_dir_name(obs_type, react_dict)


def resonance_spacing(pure_exfor=False):
    """
    To extract the resonance spacing (N,0),,D reactions for Arjan Koning
    """
    type = "resonance_spacing"
    targets = list_of_target(type)

    ripl_d0 = pd.DataFrame()
    ripl_d1 = pd.DataFrame()
    if not pure_exfor:
        ripl_d0 = read_ripl3_d0()
        ripl_d1 = read_ripl3_d1()

    for target in targets:
        reactions = ["N,0", "N,EL"]
        for reaction in reactions:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            df0 = pd.DataFrame()
            df1 = pd.DataFrame()
            if not pure_exfor:
                z = target.split("-")[0]
                el = target.split("-")[1].title()
                a = target.split("-")[2]
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

            dir = _obs_output_dir("resonance_spacing", react_dict, pure_exfor)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_resonance_spacing_table(
                type,
                dir,
                outfile,
                react_dict,
                df,
                df0,
                df1,
                include_reference=not pure_exfor,
            )

    return


def resonance_integral(pure_exfor=False):
    """
    To extract the resonance integral data, (N,G),,RI
    """
    reactions = ["N,TOT", "N,G", "N,P", "N,A", "N,ABS", "N,F", "N,SCT"]
    type = "resonance_integral"
    targets = list_of_target(type)

    for target in targets:
        for reaction in reactions:
            df = pd.DataFrame()
            print("resonance_integral():", target, reaction)
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            dir = _obs_output_dir("resonance_integral", react_dict, pure_exfor)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_thermal_table(
                type, dir, outfile, react_dict, df, append=not pure_exfor
            )

    return


def macs(pure_exfor=False):
    """
    To extract the Maxwellian average cross section, (N,x),,SIG,,MXW
    """
    reactions = ["N,G"]
    type = "macs"
    targets = list_of_target(type)
    for target in targets:
        for reaction in reactions:
            df = pd.DataFrame()
            print("acs():", target, reaction)
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

            dir = _obs_output_dir("macs", react_dict, pure_exfor)
            outfile = get_thermal_filename(dir, react_dict)

            write_to_thermal_table(
                type, dir, outfile, react_dict, df, append=not pure_exfor
            )

    return


def _generic_scalar_observable(obs_type, pure_exfor=False):
    target_dict = list_of_reactions_and_entries(obs_type)
    for target in target_dict:
        for reaction, entries in target_dict[target].items():
            print(f"{obs_type}():", target, reaction)
            react_dict = {"target": target, "process": reaction, "sf4": None}
            frames = [df for _, df in _iter_entry_data(obs_type, entries) if not df.empty]
            if not frames:
                continue
            df = pd.concat(frames, ignore_index=True)
            dir = _obs_output_dir(obs_type, react_dict, pure_exfor)
            outfile = get_thermal_filename(dir, react_dict)
            write_to_thermal_table(
                obs_type, dir, outfile, react_dict, df, append=not pure_exfor
            )


def level_density(pure_exfor=False):
    _generic_scalar_observable("level_density", pure_exfor=pure_exfor)


def strength_function(pure_exfor=False):
    _generic_scalar_observable("strength_function", pure_exfor=pure_exfor)


def resonance_parameter(pure_exfor=False):
    """
    Extract resonance parameter data grouped by ENTRY-SUBENT,
    combining multiple reactions horizontally.
    """

    projectiles = ["P", "A", "G", "N"]
    obs_type = "resonance_parameter"

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

            for sf6 in resonance_parameter_sf6:
                print(f"resonance_parameter Projectile: {projectile} Target: {target} SF6:{sf6}")
                react_dict = {
                    "target": target,
                    "process": f"{projectile},0",
                    "sf4": None,
                }
                df = resonance_parameter_data_query(obs_type, sf6, target, f"{projectile},0")
                print(df[["entry_id", "process", "en_inc", "den_inc", "sf6", "sf8", "data"]])
                if df.empty:
                    continue

                for (entry_subent, sf8), row in df.groupby(
                    [df["entry_id"].str[:9], df["sf8"]],
                    group_keys=False,
                    dropna=False,
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
                    react_dict["sf8"] = None if pd.isna(sf8) else sf8
                    react_dict["process"] = row["process"].unique()[0]
                    react_dict["en_res_type"] = row["en_res_type"].unique()[0]
                    react_dict["target"] = target
                    react_dict["projectile"] = projectile
                    # print(row[["entry_id", "process", "en_inc", "den_inc", "data", "ddata", "width_str", "dwidth_str"]])

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

                    dir = (
                        get_resonance_param_dir_name("resonance_parameter", react_dict)
                        if pure_exfor
                        else get_reference_resonance_param_dir_name(react_dict)
                    )
                    outfile = get_resonance_param_file_name(
                        dir, entry_subent, main_bib_dict, react_dict
                    )
                    write_to_exfortables_format_resonance_parameter(
                        entry_subent, dir, outfile, main_bib_dict, react_dict, pivot_df
                    )

    return


def _make_bib_dict(react_dict):
    """Build a flat bib dict from a DB row (as returned by data_query_by_id)."""
    return {
        "first_author": react_dict["first_author"],
        "year": react_dict["year"],
        "first_author_institute": react_dict["first_author_institute"],
        "main_facility_institute": react_dict["main_facility_institute"],
        "main_facility_type": react_dict["main_facility_type"],
        "main_reference": react_dict["main_reference"],
    }


def angular_distribution():
    """Write angular distribution (DA) files for all entries in the DB."""
    obs_type = "angular_distribution"
    target_dict = list_of_reactions_and_entries(obs_type)

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            for ent, df in _iter_entry_data(obs_type, entries):
                print("angular_distribution():", target, reaction, ent)

                react_dict = df.iloc[0].to_dict()
                if filter_angular_distribution_case(react_dict, df):
                    continue

                main_bib_dict = _make_bib_dict(react_dict)
                try:
                    if react_dict["sf5"] != "PAR":
                        process_angular_distribution_section_case(
                            df, react_dict["entry_id"], main_bib_dict, react_dict
                        )
                    elif (
                        react_dict["sf5"] == "PAR"
                        and react_dict["process"].split(",")[1] == "INL"
                    ):
                        if filter_partial_angular_distribution_case(react_dict, df):
                            continue
                        process_partial_angular_distribution_case(
                            df, react_dict["entry_id"], main_bib_dict, react_dict
                        )

                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except Exception:
                    logging.error(f"ERROR: at {ent}", exc_info=True)


def energy_distribution():
    """Write energy distribution (DE) files for all entries in the DB."""
    obs_type = "energy_distribution"
    target_dict = list_of_reactions_and_entries(obs_type)

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            for ent, df in _iter_entry_data(obs_type, entries):
                print("energy_distribution():", target, reaction, ent)

                react_dict = df.iloc[0].to_dict()
                if filter_energy_distribution_case(react_dict, df):
                    continue

                main_bib_dict = _make_bib_dict(react_dict)
                try:
                    process_energy_distribution_case(
                        df, react_dict["entry_id"], main_bib_dict, react_dict
                    )
                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except Exception:
                    logging.error(f"ERROR: at {ent}", exc_info=True)


def double_differential_cross_section():
    """Write double differential cross section (DA/DE) files for all entries in the DB."""
    obs_type = "double_differential_cross_section"
    target_dict = list_of_reactions_and_entries(obs_type)

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            for ent, df in _iter_entry_data(obs_type, entries):
                print("DDX:", target, reaction, ent)

                react_dict = df.iloc[0].to_dict()
                if filter_double_differential_cross_section_case(react_dict, df):
                    continue

                main_bib_dict = _make_bib_dict(react_dict)
                try:
                    process_double_differential_cross_section_case(
                        df, react_dict["entry_id"], main_bib_dict, react_dict
                    )
                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except Exception:
                    logging.error(f"ERROR: at {ent}", exc_info=True)


def fission_yield():
    """Write fission yield (FY) files for all entries in the DB."""
    obs_type = "fission_yield"
    target_dict = list_of_reactions_and_entries(obs_type)

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            for ent, df in _iter_entry_data(obs_type, entries):
                print("fission_yield()", target, reaction, ent)

                react_dict = df.iloc[0].to_dict()
                if filter_fission_yield_case(react_dict, df):
                    continue

                main_bib_dict = _make_bib_dict(react_dict)
                try:
                    process_fission_yield_case(
                        df, react_dict["entry_id"], main_bib_dict, react_dict
                    )
                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except Exception:
                    logging.error(f"ERROR: at {ent}", exc_info=True)


def neutron_observables():
    """Write neutron multiplicity / emission spectra (NU) files for all entries in the DB."""
    obs_type = "neutrons"
    target_dict = list_of_reactions_and_entries(obs_type)

    for target in reversed(target_dict.keys()):
        for reaction, entries in target_dict[target].items():
            for ent, df in _iter_entry_data(obs_type, entries):
                print("neutron_observables()", target, reaction, ent)

                react_dict = df.iloc[0].to_dict()
                if filter_misc_neutron_observables_case(react_dict, df):
                    continue

                main_bib_dict = _make_bib_dict(react_dict)
                try:
                    if (
                        react_dict["sf5"] == "PR"
                        and react_dict["sf6"] not in ("NU/DE", "FY/DE")
                    ):
                        process_neutron_observables_case(
                            df, react_dict["entry_id"], main_bib_dict, react_dict
                        )
                    else:
                        process_misc_neutron_observables_case(
                            df, react_dict["entry_id"], main_bib_dict, react_dict
                        )
                except KeyboardInterrupt:
                    print("CTR + C")
                    break
                except Exception:
                    logging.error(f"ERROR: at {ent}", exc_info=True)


def extract_reaction(x4_code):
    match = re.search(r"\(.*?\((N,[^)]+)\)", x4_code)
    return match.group(1).split(",")[1] if match else None


def gamma_gamma(pure_exfor=False):
    resonance_data_reaction = ["N,G"]
    type = "gamma_gamma"
    targets = list_of_target(type)

    ripl_d0 = pd.DataFrame()
    ripl_d1 = pd.DataFrame()
    if not pure_exfor:
        ripl_d0 = read_ripl3_d0()
        ripl_d1 = read_ripl3_d1()

    for target in targets:
        print("gamma_gamma()", target)
        for reaction in resonance_data_reaction:
            react_dict = {"target": target, "process": reaction, "sf4": None}
            df = observable_data_query(type, target, reaction)

            if df.empty:
                continue

            df0 = pd.DataFrame()
            df1 = pd.DataFrame()
            if not pure_exfor:
                z = target.split("-")[0]
                el = target.split("-")[1].title()
                a = target.split("-")[2]
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

            dir = _obs_output_dir("gamma_gamma", react_dict, pure_exfor)
            outfile = get_thermal_filename(dir, react_dict)
            write_to_resonance_spacing_table(
                type,
                dir,
                outfile,
                react_dict,
                df,
                df0,
                df1,
                include_reference=not pure_exfor,
            )

    return
    # write_to_resonance_spacing_table(dir, outfile, react_dict)
