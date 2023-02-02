import os
import pandas as pd
from contextlib import redirect_stdout


def write_to_exfortables_format_sig(id, dir, file, main_bib_dict, react_dict, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print(
                    "# entry           :",
                    id[0:5],
                    "\n" "# subentry        :",
                    id[5:8],
                    "\n" "# pointer         :",
                    id[8:],
                    "\n" "# reaction        :",
                    react_dict["code"],
                    "\n" "# incident energy :",
                    "{:.2e} MeV".format(df.en_inc.min())
                    + "  -  "
                    + "{:.2e} MeV".format(df.en_inc.max()),
                    "\n" "# target          :",
                    react_dict["target"],
                    "\n" "# product         :",
                    df["product"].unique()[0]
                    if not df["product"].isnull().all()
                    else "-",
                    "\n" "# author          :",
                    main_bib_dict["authors"][0]["name"],
                    "\n" "# institute       :",
                    (
                        main_bib_dict["institutes"][0]["x4_code"]
                        if main_bib_dict.get("institutes")
                        else None
                    ),
                    "\n" "# reference       :",
                    main_bib_dict["references"][0]["x4_code"]
                    if main_bib_dict.get("references")
                    else "no reference",
                    "\n" "# year            :",
                    main_bib_dict["references"][0]["publication_year"]
                    if main_bib_dict.get("references")
                    else "1900",
                    "\n" "# facility        :",
                    (
                        main_bib_dict["facilities"][0]["x4_code"]
                        if main_bib_dict.get("facilities")
                        else None
                    ),
                    # "\n" "# frame       :",
                    # df.Frame.unique()[0],
                )
                print("#")
                print("#     E_in(MeV)        dE_in(NMeV)      XS(B)            dXS(B)")
                for i, row in df.iterrows():
                    print(
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
                            row["en_inc"],
                            row["den_inc"],
                            row["data"],
                            row["ddata"],
                        )
                    )
        f.close()
    return


def write_to_exfortables_format_par_sig(id, dir, file, main_bib_dict, react_dict, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print(
                    "# entry           :",
                    id[0:5],
                    "\n" "# subentry        :",
                    id[5:8],
                    "\n" "# pointer         :",
                    id[8:],
                    "\n" "# reaction        :",
                    react_dict["code"],
                    "\n" "# incident energy :",
                    "{:.2e} MeV".format(df.en_inc.min())
                    + "  -  "
                    + "{:.2e} MeV".format(df.en_inc.max()),
                    "\n" "# target          :",
                    react_dict["target"],
                    "\n" "# product         :",
                    df["product"].unique()[0]
                    if not df["product"].isnull().all()
                    else "-",
                    "\n" "# level energy    :",
                    "{:.2e} MeV".format(df.e_outgoing.unique()[0]),
                    "\n" "# author          :",
                    main_bib_dict["authors"][0]["name"],
                    "\n" "# institute       :",
                    (
                        main_bib_dict["institutes"][0]["x4_code"]
                        if main_bib_dict.get("institutes")
                        else None
                    ),
                    "\n" "# reference       :",
                    main_bib_dict["references"][0]["x4_code"]
                    if main_bib_dict.get("references")
                    else "no reference",
                    "\n" "# year            :",
                    main_bib_dict["references"][0]["publication_year"]
                    if main_bib_dict.get("references")
                    else "1900",
                    "\n" "# facility        :",
                    (
                        main_bib_dict["facilities"][0]["x4_code"]
                        if main_bib_dict.get("facilities")
                        else None
                    ),
                    # "\n" "# frame       :",
                    # df.Frame.unique()[0],
                )
                print("#")
                print("#     E_in(MeV)        dE_in(NMeV)      XS(B)            dXS(B)")
                for i, row in df.iterrows():
                    print(
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
                            row["en_inc"],
                            row["den_inc"],
                            row["data"],
                            row["ddata"],
                        )
                    )
        f.close()
    return



def write_to_exfortables_format_da(id, dir, file, main_bib_dict, react_dict, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print(
                    "# entry           :",
                    id[0:5],
                    "\n" "# subentry        :",
                    id[5:8],
                    "\n" "# pointer         :",
                    id[8:],
                    "\n" "# reaction        :",
                    react_dict["code"],
                    "\n" "# incident energy :",
                    "{:.2e} MeV".format(df.en_inc.unique()[0]),
                    "\n" "# target          :",
                    react_dict["target"],
                    "\n" "# product         :",
                    df["product"].unique()[0]
                    if not df["product"].isnull().all()
                    else "-",
                    "\n" "# year            :",
                    main_bib_dict["references"][0]["publication_year"]
                    if main_bib_dict.get("references")
                    else "1900",
                    "\n" "# author          :",
                    main_bib_dict["authors"][0]["name"],
                    "\n" "# institute       :",
                    (
                        main_bib_dict["institutes"][0]["x4_code"]
                        if main_bib_dict.get("institutes")
                        else None
                    ),
                    "\n" "# reference       :",
                    main_bib_dict["references"][0]["x4_code"]
                    if main_bib_dict.get("references")
                    else "no facility",
                    "\n" "# facility        :",
                    (
                        main_bib_dict["facilities"][0]["x4_code"]
                        if main_bib_dict.get("facilities")
                        else None
                    ),
                    "\n" "# frame           :",
                    # df.Frame.unique()[0],
                )
                print("#")
                print("# Angle(dgrees)    dAngle(dgrees)  XS(barns/steradian)  dXS(barns/steradian)")
                for i, row in df.iterrows():
                    print(
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
                            row["angle"],
                            row["dangle"],
                            row["data"],
                            row["ddata"],
                        )
                    )
        f.close()
    return




def write_to_exfortables_format_par_da(id, dir, file, main_bib_dict, react_dict, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print(
                    "# entry           :",
                    id[0:5],
                    "\n" "# subentry        :",
                    id[5:8],
                    "\n" "# pointer         :",
                    id[8:],
                    "\n" "# reaction        :",
                    react_dict["code"],
                    "\n" "# incident energy :",
                    "{:.2e} MeV".format(df.en_inc.unique()[0]),
                    "\n" "# target          :",
                    react_dict["target"],
                    "\n" "# product         :",
                    df["product"].unique()[0]
                    if not df["product"].isnull().all()
                    else "-",
                    "\n" "# year            :",
                    main_bib_dict["references"][0]["publication_year"]
                    if main_bib_dict.get("references")
                    else "1900",
                    "\n" "# author          :",
                    main_bib_dict["authors"][0]["name"],
                    "\n" "# institute       :",
                    (
                        main_bib_dict["institutes"][0]["x4_code"]
                        if main_bib_dict.get("institutes")
                        else None
                    ),
                    "\n" "# reference       :",
                    main_bib_dict["references"][0]["x4_code"]
                    if main_bib_dict.get("references")
                    else "no facility",
                    "\n" "# facility        :",
                    (
                        main_bib_dict["facilities"][0]["x4_code"]
                        if main_bib_dict.get("facilities")
                        else None
                    ),
                    "\n" "# frame           :",
                    # df.Frame.unique()[0],
                )
                print("#")
                print("# Angle(dgrees)    dAngle(dgrees)  XS(barns/steradian)  dXS(barns/steradian)")
                for i, row in df.iterrows():
                    print(
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
                            row["angle"],
                            row["dangle"],
                            row["data"],
                            row["ddata"],
                        )
                    )
        f.close()
    return




def write_to_exfortables_format_fy(id, dir, file, main_bib_dict, react_dict, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print(
                    "# entry           :",
                    id[0:5],
                    "\n" "# subentry        :",
                    id[5:8],
                    "\n" "# pointer         :",
                    id[8:],
                    "\n" "# reaction        :",
                    react_dict["code"],
                    "\n" "# incident energy :",
                    "{:.2e} MeV".format(df.en_inc.unique()[0]),
                    "\n" "# year            :",
                    main_bib_dict["references"][0]["publication_year"],
                    "\n" "# author          :",
                    main_bib_dict["authors"][0]["name"],
                    "\n" "# institute       :",
                    (
                        main_bib_dict["institutes"][0]["x4_code"]
                        if main_bib_dict.get("institutes")
                        else None
                    ),
                    "\n" "# reference       :",
                    main_bib_dict["references"][0]["x4_code"],
                    "\n" "# facility        :",
                    (
                        main_bib_dict["facilities"][0]["x4_code"]
                        if main_bib_dict.get("facilities")
                        else None
                    ),
                    # "\n" "# frame       :",
                    # df.Frame.unique()[0],
                )
                print("#")
                print(
                    "# Charge(No Dim.)    Mass(No Dim.)  Isomer(No Dim.)    Yield(%/fiss)   dYield(%/fiss)"
                )
                for i, row in df.iterrows():
                    print(
                        "{:>17}{:>17}{:17}{:17.5E}{:17.5E}".format(
                            row["charge"],
                            row["mass"],
                            row["isomer"],
                            row["data"],
                            row["ddata"],
                        )
                    )
        f.close()
    return




def write_to_exfortables_format_kinetic_e(id, dir, file, main_bib_dict, react_dict, df):
    ## create an output directory if it doesn't exist
    if os.path.exists(dir):
        pass

    else:
        os.makedirs(dir)

    with open(file, "w") as f:
        with pd.option_context("display.float_format", "{:11.5e}".format):
            with redirect_stdout(f):
                print(
                    "# entry           :",
                    id[0:5],
                    "\n" "# subentry        :",
                    id[5:8],
                    "\n" "# pointer         :",
                    id[8:],
                    "\n" "# reaction        :",
                    react_dict["code"],
                    "\n" "# incident energy :",
                    "{:.2e} MeV".format(df.en_inc.min())
                    + "  -  "
                    + "{:.2e} MeV".format(df.en_inc.max()),
                    "\n" "# target          :",
                    react_dict["target"],
                    "\n" "# product         :",
                    df["product"].unique()[0]
                    if not df["product"].isnull().all()
                    else "-",
                    "\n" "# author          :",
                    main_bib_dict["authors"][0]["name"],
                    "\n" "# institute       :",
                    (
                        main_bib_dict["institutes"][0]["x4_code"]
                        if main_bib_dict.get("institutes")
                        else None
                    ),
                    "\n" "# reference       :",
                    main_bib_dict["references"][0]["x4_code"]
                    if main_bib_dict.get("references")
                    else "no reference",
                    "\n" "# year            :",
                    main_bib_dict["references"][0]["publication_year"]
                    if main_bib_dict.get("references")
                    else "1900",
                    "\n" "# facility        :",
                    (
                        main_bib_dict["facilities"][0]["x4_code"]
                        if main_bib_dict.get("facilities")
                        else None
                    ),
                    # "\n" "# frame       :",
                    # df.Frame.unique()[0],
                )
                print("#")
                print("#     E_in(MeV)        dE_in(NMeV)      Energy(MeV)            dEnergy(MeV)")
                for i, row in df.iterrows():
                    print(
                        "{:17.5E}{:17.5E}{:17.5E}{:17.5E}".format(
                            row["en_inc"],
                            row["den_inc"],
                            row["data"],
                            row["ddata"],
                        )
                    )
        f.close()
    return





