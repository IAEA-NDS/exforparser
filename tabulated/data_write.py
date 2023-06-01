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
import pandas as pd
from contextlib import redirect_stdout

from .data_dir_files import target_reformat
from exfor_dictionary import Diction
D = Diction()

def bib_table(id, main_bib_dict, react_dict, mfmt, df):
    print(
        "# entry-subent-pointer  :",
        id,
        "\n" "# EXFOR reaction        :",
        react_dict["code"],
        "\n" "# incident energy       :",
        (
            "{:.2e} MeV".format(df.en_inc.min())
            + " - "
            + "{:.2e} MeV".format(df.en_inc.max())
            if len(df["en_inc"].unique()) > 1
            else "{:.2e} MeV".format(df["en_inc"].unique()[0])
        ),
        "\n" "# target                :",
        target_reformat(react_dict),
        "\n" "# product               :",
        (
            "-"
            if df["residual"].isnull().all()
            else df["residual"].unique()[0]
            if len(df["residual"].unique()) == 1
            and not pd.isnull(df["residual"].unique())
            else str(df.mass.min()) + " <= A <= " + str(df.mass.max())
            if "A=" in df["residual"].unique()[0]
            else str(df.charge.min()) + " <= Z <= " + str(df.charge.max())
            if "Z=" in df["residual"].unique()[0]
            else "-"
        ),
        "\n" "# level energy          :",
        "{:.2e} MeV".format(df.e_out.unique()[0])
        if not df["e_out"].isnull().all()
        else "-",
        "\n" "# MF-MT number          :",
        mfmt,
        "\n" "# first author          :",
        main_bib_dict["authors"][0]["name"],
        "\n" "# institute             :",
        (
            main_bib_dict["institutes"][0]["x4_code"]
            + ": "
            + D.get_institute(main_bib_dict["institutes"][0]["x4_code"])
            if main_bib_dict.get("institutes")
            else None
        ),
        "\n" "# reference             :",
        main_bib_dict["references"][0]["x4_code"]
        if main_bib_dict.get("references")
        else "no reference",
        "\n" "# year                  :",
        main_bib_dict["references"][0]["publication_year"]
        if main_bib_dict.get("references")
        else "no info",
        "\n" "# facility              :",
        (
            main_bib_dict["facilities"][0]["facility_type"]
            + ": "
            + D.get_facility(main_bib_dict["facilities"][0]["facility_type"])
            if main_bib_dict.get("facilities")
            and main_bib_dict["facilities"][0].get("facility_type")
            else None
            + " in "
            + main_bib_dict["facilities"][0]["institute"]
            + ": "
            + D.get_facility(main_bib_dict["facilities"][0]["institute"])
            if main_bib_dict.get("facilities")
            and main_bib_dict["facilities"][0].get("institute")
            else main_bib_dict["facilities"][0]["x4_code"]
            if main_bib_dict.get("facilities")
            else None
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
                    "#       E_in(MeV)       dE_in(MeV)            XS(B)           dXS(B)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
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
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
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
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
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
                        "{:>17}{:>17}{:17}{:17.5E}{:17.5E}".format(
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
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
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
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
                            row["en_inc"],
                            0.0 if pd.isnull(row["den_inc"]) else row["den_inc"],
                            row["data"],
                            0.0 if pd.isnull(row["ddata"]) else row["ddata"],
                        )
                    )
        f.close()
    return
