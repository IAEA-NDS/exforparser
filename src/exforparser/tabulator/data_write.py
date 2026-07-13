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
import json
import numbers
import numpy as np
import pandas as pd
from contextlib import redirect_stdout
from datetime import datetime

from .data_dir_files import target_reformat
from .data_stat import thermal_mean
from exfor_dictionary.exfor_dict import Diction


d = Diction("35")
sf9_list = d.get_diction()


def _dict_desc(method, fallback_method, code):
    for name in (method, fallback_method):
        func = getattr(d, name, None)
        if not func:
            continue
        try:
            return func(code)
        except KeyError:
            return code
    return code


def _institute_desc(code):
    return _dict_desc("get_institute", "get_institute_desc", code)


def _facility_desc(code):
    return _dict_desc("get_facility", "get_facility_desc", code)


def bib_table_original(entry_id, main_bib_dict, react_dict, mfmt, df):
    print(
        "# Entry-Subent-Pointer  :",
        entry_id,
        "\n" "# EXFOR reaction        :",
        react_dict["x4_code"],
        "\n" "# Incident energy       :",
        (
            "{:.4e} MeV".format(df.en_inc.min() / 1e6)
            + " - "
            + "{:.4e} MeV".format(df.en_inc.max() / 1e6)
            if len(df["en_inc"].unique()) > 1
            else "{:.4e} MeV".format(df["en_inc"].unique()[0] / 1e6)
        ),
        "\n" "# target                :",
        target_reformat(react_dict),
        "\n" "# product               :",
        (
            "-"
            if df["residual"].isnull().all()
            else (
                df["residual"].unique()[0]
                if len(df["residual"].unique()) == 1
                and not pd.isnull(df["residual"].unique())
                else (
                    str(df.mass.min()) + " <= A <= " + str(df.mass.max())
                    if "A=" in df["residual"].unique()[0]
                    else (
                        str(df.charge.min()) + " <= Z <= " + str(df.charge.max())
                        if "Z=" in df["residual"].unique()[0]
                        else "-"
                    )
                )
            )
        ),
        "\n" "# level energy          :",
        (
            "{:.4e} MeV".format(df.e_out.unique()[0] / 1e6)
            if not df["e_out"].isnull().all()
            else "-"
        ),
        "\n" "# MF-MT number          :",
        mfmt,
        "\n" "# first author          :",
        main_bib_dict["authors"][0]["name"],
        "\n" "# institute             :",
        (
            main_bib_dict["institutes"][0]["x4_code"]
            + ": "
            + _institute_desc(main_bib_dict["institutes"][0]["x4_code"])
            if main_bib_dict.get("institutes")
            else None
        ),
        "\n" "# reference             :",
        (
            main_bib_dict["references"][0]["x4_code"]
            if main_bib_dict.get("references")
            else "no reference"
        ),
        "\n" "# year                  :",
        (
            main_bib_dict["references"][0]["publication_year"]
            if main_bib_dict.get("references")
            else "no info"
        ),
        "\n" "# facility              :",
        (
            main_bib_dict["facilities"][0]["facility_type"]
            + ": "
            + _facility_desc(main_bib_dict["facilities"][0]["facility_type"])
            if main_bib_dict.get("facilities")
            and main_bib_dict["facilities"][0].get("facility_type")
            else (
                main_bib_dict["facilities"][0]["institute"]
                + ": "
                + _facility_desc(main_bib_dict["facilities"][0]["institute"])
                if main_bib_dict.get("facilities")
                and main_bib_dict["facilities"][0].get("institute")
                else (
                    main_bib_dict["facilities"][0]["x4_code"]
                    if main_bib_dict.get("facilities")
                    else None
                )
            )
        ),
        "\n" "# git                   :",
        "https://github.com/IAEA-NDS/exfor_master/blob/main/exforall/"
        + entry_id[:3]
        + "/"
        + entry_id[0:5]
        + ".x4",
        "\n" "# nds                   :",
        "https://nds.iaea.org/EXFOR/" + entry_id[0:5],
    )


def _first_nonnull(df, column, default=None):
    if column not in df.columns:
        return default
    values = df[column].dropna().unique()
    return values[0] if len(values) else default


def _unit_label(df, unit_column, default):
    unit = _first_nonnull(df, unit_column)
    return unit if unit else default


def _frame_label(frame):
    if frame in (True, 1, "1"):
        return "CM"
    if frame in (False, 0, "0"):
        return None
    return str(frame).upper() if frame else None


def _frame_suffix(df, column):
    frame = _frame_label(_first_nonnull(df, column))
    return f"_{frame.lower()}" if frame else ""


def _en_inc_header(df):
    return f"E_in{_frame_suffix(df, 'en_inc_frame')}(MeV)"


def _den_inc_header(df):
    return f"dE_in{_frame_suffix(df, 'en_inc_frame')}(MeV)"


def _e_out_header(df):
    return f"E_out{_frame_suffix(df, 'e_out_frame')}(MeV)"


def _de_out_header(df):
    return f"dE_out{_frame_suffix(df, 'e_out_frame')}(MeV)"


def _angle_header(df):
    return f"Angle{_frame_suffix(df, 'angle_frame')}(degrees)"


def _dangle_header(df):
    return f"dAngle{_frame_suffix(df, 'angle_frame')}(degrees)"


def _data_header(df, default_unit, label="data"):
    head = str(_first_nonnull(df, "y_head", label)).lower().replace("-", "_")
    unit = _unit_label(df, "y_unit", default_unit)
    return f"{head}({unit})"


def _uncertainty_header(df, default_unit):
    return "d" + _data_header(df, default_unit)


def _sf6_title(sf6):
    titles = {
        "SIG": "Cross section",
        "DA": "Angular distribution",
        "DE": "Energy distribution",
        "DA/DE": "Double differential cross section",
        "FY": "Fission yield",
        "TRN": "Transmission",
    }
    if sf6 in titles:
        return titles[sf6]
    if sf6 == "DA/DE":
        return "Double differential cross section"
    try:
        return d.get_sf6(sf6)
    except (AttributeError, KeyError):
        return sf6


def bib_table(entry_id, main_bib_dict, react_dict, mfmt, df):
    today = datetime.today().strftime("%Y-%m-%d")
    print(
        "# Header:",
        "\n"
        f"#   Title: {react_dict['target']}({react_dict['process']})  {_sf6_title(react_dict['sf6'])}",
        "\n" f"#   Source: EXFOR",
        "\n" f"#   Date created: {str(today)}",
        "\n" f"# Target:",
        "\n" f"#   Z: {react_dict['target'].split('-')[0]}",
        "\n" f"#   A: {react_dict['target'].split('-')[2]}",
        "\n" f"#   Nuclide: {react_dict['target']}",
        "\n" f"# Reaction:",
        "\n" f"#   Process: {react_dict['process']}",
        "\n" f"#   MF-MT number: {mfmt}",
        "\n" f"#   Incident energy: ",
        (
            "{:.4e} MeV".format(df.en_inc.min() / 1e6)
            + " - "
            + "{:.4e} MeV".format(df.en_inc.max() / 1e6)
            if len(df["en_inc"].dropna().unique()) > 1
            else "{:.4e} MeV".format(df["en_inc"].dropna().unique()[0] / 1e6)
            if len(df["en_inc"].dropna().unique()) == 1
            else "N/A"
        ),
        "\n" f"# Residual:",
        "\n"
        f"#   Z: {react_dict['sf4'].split('-')[0] if react_dict['sf4'] and react_dict['sf4'][0].isdigit() else ''}",
        "\n"
        f"#   A: {react_dict['sf4'].split('-')[2] if react_dict['sf4'] and react_dict['sf4'][0].isdigit() else ''}",
        "\n" f"#   Nuclide: {react_dict['sf4'] if react_dict['sf4'] else ''}",
        (
            "\n#   Outgoing energy: "
            if react_dict["sf6"] in ("DE", "DA/DE")
            else "\n#   Level energy:"
        ),
        (
            "{:.4e} MeV - {:.4e} MeV".format(
                df["e_out"].min() / 1e6, df["e_out"].max() / 1e6
            )
            if react_dict["sf6"] in ("DE", "DA/DE")
            and "e_out" in df
            and not df["e_out"].isnull().all()
            else "{:.4e} MeV".format(df.e_out.unique()[0] / 1e6)
            if react_dict["sf6"] not in ("DE", "DA/DE")
            and not df["e_out"].isnull().all()
            else "-"
        ),
        "\n" "# EXFOR BIB:" "\n" f"#   Entry id: {entry_id} (entry-subentry-pointer)",
        "\n" f"#   Reaction code: {react_dict['x4_code']}",
        "\n" f"#   First author: {main_bib_dict['first_author']}",
        "\n" "#   Institute: ",
        (
            main_bib_dict["first_author_institute"]
            + ": "
            + _institute_desc(main_bib_dict["first_author_institute"])
            if main_bib_dict.get("first_author_institute")
            else None
        ),
        "\n" "#   Reference: ",
        (
            main_bib_dict["main_reference"]
            if main_bib_dict.get("main_reference")
            else "no reference"
        ),
        "\n" "#   Year: ",
        (main_bib_dict["year"] if main_bib_dict.get("year") else "no info"),
        "\n" "#   Facility: ",
        (
            main_bib_dict["main_facility_type"]
            + ": "
            + _facility_desc(main_bib_dict["main_facility_type"])
            if main_bib_dict.get("main_facility_type")
            else (
                main_bib_dict["main_facility_institute"]
                + ": "
                + _facility_desc(main_bib_dict["main_facility_institute"])
                if main_bib_dict.get("main_facility_institute")
                else None
            )
        ),
        "\n" "#   Master file: ",
        "https://github.com/IAEA-NDS/exfor_master/blob/main/exforall/"
        + entry_id[:3]
        + "/"
        + entry_id[0:5]
        + ".x4",
        "\n" "#   nds: ",
        "https://nds.iaea.org/EXFOR/" + entry_id[0:5],
    )


def bib_table_resonance_parameter(entry_id, main_bib_dict, react_dict, mfmt, df):
    today = datetime.today().strftime("%Y-%m-%d")
    parts = react_dict['target'].split('-')
    charge = parts[0]
    elem = parts[1]
    mass = parts[2]
    isomer = parts[3] if len(parts) == 4 else ""   # 4 要素あるときだけ index 3 を使う

    print(
        f"# Header:",
        "\n" f"#   Title                 : {react_dict['target']} "
            f"Resonance Parameter: {react_dict['sf6']}"
            f"{',,' + react_dict['sf8'] if react_dict.get('sf8') else ''}",
        "\n" f"#   Source                : EXFOR",
        "\n" f"#   Date Created          : {str(today)}",
        "\n" f"# EXFOR Bibliographic Information:",
        "\n" f"#   Entry-Subent-Pointer  : {react_dict['entry_id']}",
        "\n"  "#   First Author          :",
            main_bib_dict["authors"][0]["name"],
        "\n" "#   Institute             :",
        (
            main_bib_dict["first_author_institute"]
            + ": "
            + _institute_desc(main_bib_dict["first_author_institute"])
            if main_bib_dict.get("first_author_institute")
            else None
        ),
        "\n" "#   Reference             :",
        (
            main_bib_dict["main_reference"]
            if main_bib_dict.get("main_reference")
            else "no reference"
        ),
        "\n" "#   Year                  :",
        (main_bib_dict["year"] if main_bib_dict.get("year") else "no info"),
        "\n" "#   Facility              :",
        (
            main_bib_dict["main_facility_type"]
            + ": "
            + _facility_desc(main_bib_dict["main_facility_type"])
            if main_bib_dict.get("main_facility_type")
            else (
                None
                + " in "
                + main_bib_dict["main_facility_institute"]
                + ": "
                + _facility_desc(main_bib_dict["main_facility_institute"])
                if main_bib_dict.get("main_facility_institute")
                else None
            )
        ),
        "\n" f"# Target:",
        "\n" f"#   Z                     : {charge}",
        "\n" f"#   A                     : {mass}",
        "\n" f"#   Isomer                : {isomer}",
        "\n" f"#   Nuclide               : {react_dict['target']}",
        "\n" f"# Reaction:",
        "\n" f"#   EXFOR Reaction        : {react_dict['x4_code']}",
        "\n"  "#   Incident Energy       :",
        (
            "{:.4e} eV".format(df.en_inc.min())
            + " - "
            + "{:.4e} eV".format(df.en_inc.max())
            if len(df["en_inc"].unique()) > 1
            else "{:.4e} eV".format(df["en_inc"].unique()[0])
        ),
        "\n" f"#   Resonance Energy Type : {react_dict['en_res_type']}",
        "\n" f"# Links:",
        "\n"  "#   git                   :",
        "https://github.com/IAEA-NDS/exfor_master/blob/main/exforall/"
        + entry_id[:3]
        + "/"
        + entry_id[0:5]
        + ".x4",
        "\n" "#   nds                   :",
        "https://nds.iaea.org/EXFOR/" + entry_id[0:5],
    )


def _write_exfor_table(file, entry_id, main_bib_dict, react_dict, mt, df, column_header, fmt_row):
    """Shared writer for all exfortables-format text files.

    Writes the standard BIB header, a column label line, then one formatted
    line per DataFrame row produced by *fmt_row(row)*.
    """
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(entry_id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(column_header)
                for _, row in df.iterrows():
                    print(fmt_row(row))


def write_to_exfortables_format_sig(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        (
            f"# {_en_inc_header(df):>15} {_den_inc_header(df):>17} "
            f"{_data_header(df, 'B'):>17} "
            f"{_uncertainty_header(df, 'B'):>17}"
        ),
        lambda row: "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
            row["en_inc"] / 1e6,
            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"] / 1e6,
            row["data"],
            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
        ),
    )


def write_to_exfortables_format_da(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        (
            f"# {_angle_header(df):>15} {_dangle_header(df):>17} "
            f"{_data_header(df, 'B/SR'):>17} "
            f"{_uncertainty_header(df, 'B/SR'):>17}"
        ),
        lambda row: "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
            row["angle"],
            0.0 if pd.isnull(row["dangle"]) else row["dangle"],
            row["data"],
            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
        ),
    )


def write_to_exfortables_format_de(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        (
            f"# {_e_out_header(df):>15} {_de_out_header(df):>17} "
            f"{_data_header(df, 'B/EV'):>17} "
            f"{_uncertainty_header(df, 'B/EV'):>17}"
        ),
        lambda row: "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
            np.nan if pd.isnull(row["e_out"]) else row["e_out"] / 1e6,
            0.0 if pd.isnull(row["de_out"]) else row["de_out"] / 1e6,
            row["data"],
            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
        ),
    )


def write_to_exfortables_format_ddx(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        (
            f"# {_e_out_header(df):>15} {_de_out_header(df):>17} "
            f"{_angle_header(df):>17} {_dangle_header(df):>17} "
            f"{_data_header(df, 'B/SR/EV'):>17} "
            f"{_uncertainty_header(df, 'B/SR/EV'):>17}"
        ),
        lambda row: "{:18.4E}{:18.4E}{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
            np.nan if pd.isnull(row["e_out"]) else row["e_out"] / 1e6,
            0.0 if pd.isnull(row["de_out"]) else row["de_out"] / 1e6,
            np.nan if pd.isnull(row["angle"]) else row["angle"],
            0.0 if pd.isnull(row["dangle"]) else row["dangle"],
            row["data"],
            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
        ),
    )


def write_to_exfortables_format_fy(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        "# Charge(No Dim.)    Mass(No Dim.)  Isomer(No Dim.)    Yield(%/fiss)   dYield(%/fiss)",
        lambda row: "{:>17}{:>17}{:17}{:18.4E}{:18.4E}".format(
            "" if pd.isnull(row["charge"]) else row["charge"],
            "" if pd.isnull(row["mass"]) else row["mass"],
            "" if pd.isnull(row["isomer"]) else row["isomer"],
            row["data"],
            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
        ),
    )


def write_to_exfortables_format_nu(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        (
            f"# {_en_inc_header(df):>15} {_den_inc_header(df):>17} "
            f"{'Multiplicity':>17} {'dMultiplicity':>17}"
        ),
        lambda row: "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
            row["en_inc"] / 1e6,
            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"] / 1e6,
            row["data"],
            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
        ),
    )


def write_to_exfortables_format_kinetic_e(entry_id, dir, file, main_bib_dict, react_dict, mt, df):
    _write_exfor_table(
        file, entry_id, main_bib_dict, react_dict, mt, df,
        (
            f"# {_en_inc_header(df):>15} {_den_inc_header(df):>17} "
            f"{_data_header(df, 'EV'):>17} "
            f"{_uncertainty_header(df, 'EV'):>17}"
        ),
        lambda row: "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
            row["en_inc"] / 1e6,
            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"] / 1e6,
            row["data"] / 1e6,
            0.0 if pd.isnull(row["ddata"]) else row["ddata"] / 1e6,
        ),
    )


def write_to_exfortables_format_resonance_parameter(
    entry_id, dir, file, main_bib_dict, react_dict, df
):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    # projectile = react_dict["process"][next(iter(react_dict["process"]))].split(",")[0].upper()
    projectile = react_dict["process"].split(",")[0].upper()
    mfmt = "2 - x"
    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table_resonance_parameter(
                    entry_id, main_bib_dict, react_dict, mfmt, df
                )
                print("#")
                print(
                    f"#    E_in(eV)    dE_in(eV)          J          L      ({projectile},TOT)     d({projectile},TOT)        ({projectile},G)       d({projectile},G)        ({projectile},EL)     d({projectile},EL)        ({projectile},F)       d({projectile},F)        ({projectile},A)       d({projectile},A)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:13.4E}{:13.4E}{:11.1F}{:11.1F}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:13.4E}".format(
                            row["en_inc"],
                            row["den_inc"],
                            row["spin_j"],
                            row["momentum_l"],
                            row[f"data({projectile},TOT)"],
                            row[f"ddata({projectile},TOT)"],
                            row[f"data({projectile},G)"],
                            row[f"ddata({projectile},G)"],
                            row[f"data({projectile},EL)"],
                            row[f"ddata({projectile},EL)"],
                            row[f"data({projectile},F)"],
                            row[f"ddata({projectile},F)"],
                            row[f"data({projectile},A)"],
                            row[f"ddata({projectile},A)"],
                        )
                    )
        f.close()
    return


def write_to_thermal_table(obs_type, dir, outfile, react_dict, df, append=True):

    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    stat_dict = thermal_mean(obs_type, df)
    # print(json.dumps(stat_dict, indent=1))
    today = datetime.today().strftime("%Y-%m-%d")
    en_values = df["en_inc"].dropna() if "en_inc" in df else pd.Series(dtype=float)
    if len(en_values.unique()) > 1:
        incident_energy = (
            "{:.4e} MeV".format(en_values.min() / 1e6)
            + " - "
            + "{:.4e} MeV".format(en_values.max() / 1e6)
        )
    elif len(en_values.unique()) == 1:
        incident_energy = "{:.4e} MeV".format(en_values.unique()[0] / 1e6)
    else:
        incident_energy = "N/A"
    data_units = df["y_unit"].dropna().unique() if "y_unit" in df else []
    data_unit = data_units[0] if len(data_units) == 1 else "B"
    obs_title = (
        f"{obs_type} cross section"
        if obs_type in ("thermal", "resonance_integral", "macs")
        else obs_type.replace("_", " ")
    )

    with open(outfile, "a" if append else "w") as f:
        ## must be addition mode because the reaction production are different
        with redirect_stdout(f):
            print(
                f"# Header:",
                "\n"
                f"#   title: {react_dict['target']}({react_dict['process']}) {obs_title}",
                "\n" f"#   source: EXFOR",
                "\n" f"#   date created: {str(today)}",
                "\n" f"# Target:",
                "\n" f"#   Z: {react_dict['target'].split('-')[0]}",
                "\n" f"#   A: {react_dict['target'].split('-')[2]}",
                "\n" f"#   Nuclide: {react_dict['target']}",
                "\n" f"# Reaction:",
                "\n" f"#   Type: {react_dict['process']}",
                "\n" f"#   Type: {react_dict['process']}",
                "\n" f"#   Incident energy       :",
                incident_energy,
                "\n" f"# Residual:",
                "\n"
                f"#   Z: {react_dict['sf4'].split('-')[0] if react_dict['sf4'] and react_dict['sf4'][0].isdigit() else ''}",
                "\n"
                f"#   A: {react_dict['sf4'].split('-')[2] if react_dict['sf4'] and react_dict['sf4'][0].isdigit() else ''}",
                "\n" f"#   Nuclide: {react_dict['sf4'] if react_dict['sf4'] else ''}",
            )
            if stat_dict:
                print("# Statistics:")
                for k in stat_dict.keys():
                    print(
                        "{:28}{:^5}{:20}{:1}{:12.5E}{:^5}{:12.5E}{:>10}\n{:28}{:^5}{:20}{:1}{:12.5E}{:^5}{:12.5E}{:>10}".format(
                            "#   " + k + " Simple Mean",
                            "|",
                            "Simple Stdev",
                            ":",
                            (
                                stat_dict[k]["simple_mean"]
                                if stat_dict[k]["simple_mean"] is not None
                                else ""
                            ),
                            "|",
                            (
                                stat_dict[k]["simple_stdev"]
                                if stat_dict[k]["simple_stdev"] is not None
                                else ""
                            ),
                            f"(N = {stat_dict[k]['np']})",
                            "#   " + k + " Weighted Mean",
                            "+/-",
                            "Weighted Error",
                            ":",
                            (
                                stat_dict[k]["weighted_mean"]
                                if stat_dict[k]["weighted_mean"] is not None
                                else ""
                            ),
                            "+/-",
                            (
                                stat_dict[k]["weighted_error"]
                                if stat_dict[k]["weighted_error"] is not None
                                else ""
                            ),
                            f"(N = {stat_dict[k]['np']})",
                        )
                    )
            print("#\n# Data Table")
            for sf9 in [0, 1]:
                if sf9 == 0:
                    df_sf9 = df[df["sf9"].isna()]
                elif sf9 == 1:
                    df_sf9 = df[df["sf9"].isin(sf9_list)]

                if not df_sf9.empty:
                    if sf9 == 0:
                        print("#   Experimental Data")
                    elif sf9 == 1:
                        print("#   Recom./Eval./Deriv./Calc. Data")

                    print(
                        f"# EXFOR ID          First Author            Year   En_inc [MeV] dEn_inc      Data [{data_unit}]     dData         sf8    sf9"
                    )
                    for i, row in df_sf9.iterrows():
                        print(
                            "{:20}{:20}{:8n}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:>8}{:>8}".format(
                                row["entry_id"],
                                row["first_author"],
                                row["year"],
                                np.nan if pd.isnull(row["en_inc"]) else row["en_inc"] / 1e6,
                                0.0 if pd.isnull(row["den_inc"]) else row["den_inc"] / 1e6,
                                row["data"],
                                0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                                "" if pd.isnull(row["sf8"]) else row["sf8"],
                                "" if pd.isnull(row["sf9"]) else row["sf9"],
                            )
                        )
            #         print("# ------------------")
            # print("#\n")
    f.close()
    return


def write_to_resonance_spacing_table(
    type, dir, outfile, react_dict, df, df0=None, df1=None, include_reference=True
):

    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    if type == "resonance_spacing":
        type_desc = "Level Spacing (SF6='D' in EXFOR)"

    elif type == "gamma_gamma":
        type_desc = "gamma_gamma (,,WID,,AV) in EXFOR"

    today = datetime.today().strftime("%Y-%m-%d")

    with open(outfile, "w") as f:
        with redirect_stdout(f):
            print(
                f"# Header:",
                "\n"
                f"#   title: {react_dict['target']}({react_dict['process']}) {type_desc}",
                "\n" f"#   source: EXFOR",
                "\n" f"#   date created: {str(today)}",
                "\n" f"# Target:",
                "\n" f"#   Z: {react_dict['target'].split('-')[0]}",
                "\n" f"#   A: {react_dict['target'].split('-')[2]}",
                "\n" f"#   Nuclide: {react_dict['target']}",
                "\n" f"# Reaction:",
                "\n" f"#   Type: {react_dict['process']}",
            )

            print("#\n# Data Table")
            print("## Experimental Data")
            print(
                "# EXFOR ID          First Author            Year   En_min[MeV]  En_max [MeV] Data [eV]    dData [eV]        Momentum L   SPIN J       PARITY"
            )
            for i, row in df.iterrows():
                flags = row["flags"]
                if flags:
                    flags = json.loads(flags)
                else:
                    flags = {}
                print(
                    "{:20}{:20}{:8n}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:11.1F}{:13.1F}{:13.1F}".format(
                        row["entry_id"],
                        row["first_author"],
                        row["year"],
                        np.nan if not row["en_inc_min"] else row["en_inc_min"] / 1e6,
                        np.nan if not row["en_inc_max"] else row["en_inc_max"] / 1e6,
                        row["data"],
                        np.nan if pd.isnull(row["ddata"]) else row["ddata"],
                        (
                            flags["MOMENTUM L"]["data"]
                            if flags.get("MOMENTUM L")
                            and isinstance(flags["MOMENTUM L"]["data"], numbers.Number)
                            else np.nan
                        ),
                        (
                            flags["SPIN J"]["data"]
                            if flags.get("SPIN J")
                            and isinstance(flags["SPIN J"]["data"], numbers.Number)
                            else np.nan
                        ),
                        (
                            flags["PARITY"]["data"]
                            if flags.get("PARITY")
                            and isinstance(flags["PARITY"]["data"], numbers.Number)
                            else np.nan
                        ),
                    )
                )
            if include_reference:
                df0 = pd.DataFrame() if df0 is None else df0
                df1 = pd.DataFrame() if df1 is None else df1
                print("\n\n")
                print("## RIPL3 Data")
                print(
                    "# ID                First Author            Year   En_min[MeV]  En_max [MeV]  Data [eV]   dData [eV]        Momentum L"
                )
                print(
                    "{:20}{:20}{:8n}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:11.1F}".format(
                        "RIPL-3 D0" if type == "resonance_spacing" else "RIPL-3 Gg",
                        "A.V. Ignatyuk",
                        2009,
                        np.nan,
                        np.nan,
                        (
                            df0["D0"].values[0]
                            if not df0.empty and type == "resonance_spacing"
                            else df0["Gg"].values[0] if not df0.empty else np.nan
                        ),
                        (
                            df0["dD"].values[0]
                            if not df0.empty and type == "resonance_spacing"
                            else df0["dG"].values[0] if not df0.empty else np.nan
                        ),
                        0,
                    )
                )
                print(
                    "{:20}{:20}{:8n}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:11.1F}".format(
                        "RIPL-3 D1" if type == "resonance_spacing" else "RIPL-3 Gg1",
                        "A.V. Ignatyuk",
                        2009,
                        np.nan,
                        np.nan,
                        (
                            df1["D1"].values[0]
                            if not df1.empty and type == "resonance_spacing"
                            else df1["Gg"].values[0] if not df1.empty else np.nan
                        ),
                        (
                            df1["dD"].values[0]
                            if not df1.empty and type == "resonance_spacing"
                            else df1["dG"].values[0] if not df1.empty else np.nan
                        ),
                        1.0,
                    )
                )

    f.close()
    return
