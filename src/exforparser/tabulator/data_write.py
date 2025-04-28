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


def bib_table_original(id, main_bib_dict, react_dict, mfmt, df):
    print(
        "# entry-subent-pointer  :",
        id,
        "\n" "# EXFOR reaction        :",
        react_dict["x4_code"],
        "\n" "# incident energy       :",
        (
            "{:.4e} MeV".format(df.en_inc.min())
            + " - "
            + "{:.4e} MeV".format(df.en_inc.max())
            if len(df["en_inc"].unique()) > 1
            else "{:.4e} MeV".format(df["en_inc"].unique()[0])
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
            "{:.4e} MeV".format(df.e_out.unique()[0])
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
            + d.get_institute(main_bib_dict["institutes"][0]["x4_code"])
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
            + d.get_facility(main_bib_dict["facilities"][0]["facility_type"])
            if main_bib_dict.get("facilities")
            and main_bib_dict["facilities"][0].get("facility_type")
            else (
                None
                + " in "
                + main_bib_dict["facilities"][0]["institute"]
                + ": "
                + d.get_facility(main_bib_dict["facilities"][0]["institute"])
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
        + id[:3]
        + "/"
        + id[0:5]
        + ".x4",
        "\n" "# nds                   :",
        "https://nds.iaea.org/EXFOR/" + id[0:5],
    )



def bib_table(id, main_bib_dict, react_dict, mfmt, df):
    print(
        "# entry-subent-pointer  :",
        id,
        "\n" "# EXFOR reaction        :",
        react_dict["x4_code"],
        "\n" "# incident energy       :",
        (
            "{:.4e} MeV".format(df.en_inc.min())
            + " - "
            + "{:.4e} MeV".format(df.en_inc.max())
            if len(df["en_inc"].unique()) > 1
            else "{:.4e} MeV".format(df["en_inc"].unique()[0])
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
            "{:.4e} MeV".format(df.e_out.unique()[0])
            if not df["e_out"].isnull().all()
            else "-"
        ),
        "\n" "# MF-MT number          :",
        mfmt,
        "\n" "# first author          :",
        main_bib_dict["first_author"],
        "\n" "# institute             :",
        (
            main_bib_dict["first_author_institute"]
            + ": "
            + d.get_institute(main_bib_dict["first_author_institute"])
            if main_bib_dict.get("first_author_institute")
            else None
        ),
        "\n" "# reference             :",
        (
            main_bib_dict["main_reference"]
            if main_bib_dict.get("main_reference")
            else "no reference"
        ),
        "\n" "# year                  :",
        (
            main_bib_dict["year"]
            if main_bib_dict.get("year")
            else "no info"
        ),
        "\n" "# facility              :",
        (
            main_bib_dict["main_facility_type"]
            + ": "
            + d.get_facility(main_bib_dict["main_facility_type"])
            if main_bib_dict.get("main_facility_type")
            else (
                None
                + " in "
                + main_bib_dict["main_facility_institute"]
                + ": "
                + d.get_facility(main_bib_dict["main_facility_institute"])
                if main_bib_dict.get("main_facility_institute")
                else  None
            )
        ),
        "\n" "# git                   :",
        "https://github.com/IAEA-NDS/exfor_master/blob/main/exforall/"
        + id[:3]
        + "/"
        + id[0:5]
        + ".x4",
        "\n" "# nds                   :",
        "https://nds.iaea.org/EXFOR/" + id[0:5],
    )


def write_to_exfortables_format_sig(id, dir, file, main_bib_dict, react_dict, mt, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)
    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "#       E_in(MeV)         dE_in(MeV)        XS(B)             dXS(B)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
                            row["en_inc"],
                            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return


def write_to_exfortables_format_da(id, dir, file, main_bib_dict, react_dict, mt, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "# Angle(dgrees)     dAngle(dgrees)  XS(b/steradian)  dXS(b/steradian)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
                            row["angle"],
                            0.0 if pd.isnull(row["dangle"]) else row["dangle"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return


def write_to_exfortables_format_de(id, dir, file, main_bib_dict, react_dict, mt, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "#          E(MeV)          dE(MeV)      data(MB/MeV)   ddata(MB/MeV)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
                            row["e_out"],
                            0.0 if pd.isnull(row["de_out"]) else row["de_out"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return


def write_to_exfortables_format_fy(id, dir, file, main_bib_dict, react_dict, mt, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "# Charge(No Dim.)    Mass(No Dim.)  Isomer(No Dim.)    Yield(%/fiss)   dYield(%/fiss)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:>17}{:>17}{:17}{:18.4E}{:18.4E}".format(
                            "" if pd.isnull(row["charge"]) else row["charge"],
                            "" if pd.isnull(row["mass"]) else row["mass"],
                            "" if pd.isnull(row["isomer"]) else row["isomer"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return


def write_to_exfortables_format_nu(id, dir, file, main_bib_dict, react_dict, mt, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass
    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "#     E_in(MeV)        dE_in(MeV)       Multiplicity            dMultiplicity"
                )
                for i, row in df.iterrows():
                    print(
                        "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
                            row["en_inc"],
                            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return


def write_to_exfortables_format_kinetic_e(
    id, dir, file, main_bib_dict, react_dict, mt, df
):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "#     E_in(MeV)        dE_in(MeV)      Energy(MeV)            dEnergy(MeV)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
                            row["en_inc"],
                            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return



def write_to_exfortables_format_resonance_parameter(id, dir, file, main_bib_dict, react_dict, mt, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)
    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                bib_table(id, main_bib_dict, react_dict, mt, df)
                print("#")
                print(
                    "#       E_in(MeV)         dE_in(MeV)        XS(B)             dXS(B)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:18.4E}{:18.4E}{:18.4E}{:18.4E}".format(
                            row["en_inc"],
                            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return




def write_to_thermal_table(type, dir, outfile, react_dict, df):

    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    stat_dict = thermal_mean(type, df)
    # print(json.dumps(stat_dict, indent=1))
    today = datetime.today().strftime("%Y-%m-%d")

    with open(outfile, "a") as f:
        ## must be addition mode because the reaction production are different
        with redirect_stdout(f):
            print(
                f"# Header:",
                "\n"
                f"#   title: {react_dict['target']}({react_dict['process']}) {type} cross section",
                "\n" f"#   source: EXFOR",
                "\n" f"#   date created: {str(today)}",
                "\n" f"# Target:",
                "\n" f"#   Z: {react_dict['target'].split('-')[0]}",
                "\n" f"#   A: {react_dict['target'].split('-')[2]}",
                "\n" f"#   Nuclide: {react_dict['target']}",
                "\n" f"# Reaction:",
                "\n" f"#   Type: {react_dict['process']}",
                "\n" f"#   Incident energy       :",
                (
                    "{:.4e} MeV".format(df.en_inc.min())
                    + " - "
                    + "{:.4e} MeV".format(df.en_inc.max())
                    if len(df["en_inc"].unique()) > 1
                    else "{:.4e} MeV".format(df["en_inc"].unique()[0])
                ),
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
                        "# EXFOR ID          First Author            Year   En_inc       dEn_inc      Data         dData         sf8    sf9"
                    )
                    for i, row in df_sf9.iterrows():
                        print(
                            "{:20}{:20}{:8n}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:>8}{:>8}".format(
                                row["entry_id"],
                                row["first_author"],
                                row["year"],
                                row["en_inc"],
                                0.0 if pd.isnull(row["den_inc"]) else row["den_inc"],
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




def write_to_resonance_spacing_table(type, dir, outfile, react_dict, df, df0, df1):

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
                        np.nan if not row["en_inc_min"] else row["en_inc_min"],
                        np.nan if not row["en_inc_max"] else row["en_inc_max"],
                        row["data"],
                        np.nan if pd.isnull(row["ddata"]) else row["ddata"],
                        flags["MOMENTUM L"]["data"] if flags.get("MOMENTUM L") and isinstance(flags["MOMENTUM L"]["data"],numbers.Number) else np.nan,
                        flags["SPIN J"]["data"]     if flags.get("SPIN J")     and isinstance(flags["SPIN J"]["data"],numbers.Number) else np.nan,
                        flags["PARITY"]["data"]     if flags.get("PARITY")     and isinstance(flags["PARITY"]["data"],numbers.Number) else np.nan,

                    )
                )
            print("\n\n")
            print("## RIPL3 Data")
            print(
                "# ID                First Author            Year   En_min[MeV]  En_max [MeV] Data [eV]    dData [eV]        Momentum L"
            )
            print(
                "{:20}{:20}{:8n}{:13.4E}{:13.4E}{:13.4E}{:13.4E}{:11.1F}".format(
                    "RIPL-3 D0" if type == "resonance_spacing" else "RIPL-3 Gg",
                    "A.V. Ignatyuk",
                    2009,
                    np.nan,
                    np.nan,
                    df0['D0'].values[0]*1E+3 if  not df0.empty  and type == "resonance_spacing" else df0['Gg'].values[0]*1E+3 if not df0.empty else np.nan,
                    df0['dD'].values[0]*1E+3 if  not df0.empty  and type == "resonance_spacing" else df0['dG'].values[0]*1E+3 if not df0.empty else np.nan,
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
                    df1['D1'].values[0]*1E+3 if not df1.empty and type == "resonance_spacing" else df1['Gg'].values[0]*1E+3 if not df1.empty else np.nan,
                    df1['dD'].values[0]*1E+3 if not df1.empty and type == "resonance_spacing" else df1['dG'].values[0]*1E+3 if not df1.empty else np.nan,
                    1.0,
                )
            )


    f.close()
    return

