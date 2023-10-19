
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
import pandas as pd
import re

from ripl3_json.ripl3_discretelevel import RIPL_Level

from ..sql.queries import insert_df_to_data
from ..submodules.utilities.elem import ztoelem
from .data_locations import *
from .exfor_reaction_mt import get_mf, get_mt, e_lvl_to_mt



def limit_data_dict_by_locs(locs, data_dict):
    new = {}
    for key, val in data_dict.items():

        new[key] = []

        for loc in locs:
            new[key] += [val[loc]]

    return new


def data_length_unify(data_dict):
    data_len = []
    data_list = data_dict["data"]

    for i in data_list:
        data_len += [len(i)]

    for l in range(len(data_len)):
        if data_len[l] < max(data_len):
            data_list[l] = data_list[l] * max(data_len)

    ## Check if list length are all same
    it = iter(data_list)
    the_next = len(next(it))
    assert all(len(l) == the_next for l in it)

    ## overwrite the "data" block by extended list
    data_dict["data"] = data_list

    return data_dict


def get_decay_data():
    decay = {}
    return decay


def evaluated_data_points(**kwargs):
    new_x = []

    ## determine the first priority column
    for col in list(kwargs):
        if not kwargs[col]:
            del kwargs[col]

    for col in kwargs:

        for dl in range(len(kwargs[col])):
            lists = iter(kwargs.keys())

            if kwargs[col][dl] is None:
                a = None
                while not a:
                    # next(lists)
                    try:
                        a = kwargs[next(lists)][dl]
                    except StopIteration:
                        new_x.append(None)
                        break

                    if a is not None:
                        new_x.append(a)
                        break

                    # else:
                    #     new_x.append(None)
                    #     break

            else:
                a = kwargs[col][dl]
                new_x.append(a)


        assert len(kwargs[col]) == len(new_x)

        return new_x


def get_average(sf4, data_dict_conv):
    # print("get_average for ", sf4)
    # DATA-MIN, DATA-MAX, EN-MIN, EN-MAX, MASS-MIN, MASS-MAX ...etc
    x = []
    x_min = []
    x_max = []
    x_mean = []
    x_average = []
    x_approx = []
    new_x = []

    for l in range(len(data_dict_conv["data"])):
        if data_dict_conv["heads"][l] == sf4 or sf4 + " " in data_dict_conv["heads"][l]:
            x = data_dict_conv["data"][l]

        elif "-MIN" in data_dict_conv["heads"][l]:
            x_min = data_dict_conv["data"][l]

        elif "-MAX" in data_dict_conv["heads"][l]:
            x_max = data_dict_conv["data"][l]

        elif "-MEAN" in data_dict_conv["heads"][l]:
            x_mean = data_dict_conv["data"][l]

        elif "-APRX" in data_dict_conv["heads"][l]:
            x_approx = data_dict_conv["data"][l]

        elif data_dict_conv["heads"][l] == data_dict_conv["heads"][l - 1]:
            ## for the case of 103250050
            x_average = [
                (a + b) / 2 if a is not None and b is not None else a or b
                for a, b in zip(
                    data_dict_conv["data"][l], data_dict_conv["data"][l - 1]
                )
            ]

    if x_min and x_max:
        x_average = [
            (min + max) / 2 if min is not None and max is not None else None
            for min, max in zip(x_min, x_max)
        ]


    elif x_min and not x_max:
        x_average = x_min


    elif not x_min and x_max:
        x_average = x_max


    new_x = evaluated_data_points(
        x=x,
        x_average=x_average,
        x_mean=x_mean,
        x_approx=x_approx,
        x_min=x_min,
        x_max=x_max,
    )

    if not new_x:
        x_temp = {}
        for i in range(len(data_dict_conv["data"])):
            x_temp["x" + str(i)] = data_dict_conv["data"][i]

        new_x = evaluated_data_points(**x_temp)

    return new_x




def process_general(entry_id, entry_json, data_dict_conv):

    entnum, subent, pointer = entry_id.split("-")
    react_dict = entry_json["reactions"][subent][pointer]["children"][0]
    
    locs = {
        "locs_en": [],
        "locs_den": [],
        "locs_elem": [],
        "locs_mass": [],
        "locs_y": [],
        "locs_dy": [],
        "locs_e": [],
        "locs_de": [],
        "locs_ang": [],
        "locs_dang": [],
    }
    mass = []
    elem = []
    charge = []
    state = []
    residual = []
    data = []
    ddata = []

    en_inc = []
    den_inc = []
    e_out = []
    de_out = []
    level_num = []
    mt = []

    angle = []
    dangle = []

    ## if the data is arbitrary unit ("ARB-UNITS") then True
    data_unit_flag = False
    ddata_unit_flag = False


    ## ----------------------------------   DATA (Y axis)    --------------------------------- ##
    ## get data column position
    ## --------------------------------------------------------------------------------------- ##
    locs["locs_y"], locs["locs_dy"] = get_y_locs(data_dict_conv)

    if not locs["locs_y"]:
        locs["locs_y"], locs["locs_dy"] = get_y_locs_by_pointer(pointer, data_dict_conv)

    if len(locs["locs_y"]) == 1:
        data = data_dict_conv["data"][locs["locs_y"][0]]

    else:
        data = get_average(
            "DATA", limit_data_dict_by_locs(locs["locs_y"], data_dict_conv)
        )

    if locs["locs_y"]:
        if any(data_dict_conv["units"][locs["locs_y"][0]] == arb for arb in ("ARB-UNITS", "NO-DIM")):
            data_unit_flag = True
            

    if locs["locs_dy"]:
        if data_dict_conv["units"][locs["locs_dy"][0]] == "PER-CENT":
            ddata = [
                y * dy / 100 if dy is not None and y is not None else None
                for y, dy in zip(data, data_dict_conv["data"][locs["locs_dy"][0]])
            ]

        elif any(data_dict_conv["units"][locs["locs_dy"][0]] == arb for arb in ("ARB-UNITS", "NO-DIM")):
            ddata_unit_flag = True


        elif (
            data_dict_conv["units"][locs["locs_y"][0]]
            == data_dict_conv["units"][locs["locs_dy"][0]]
        ):
            ddata = [
                dy if dy is not None else None
                for dy in data_dict_conv["data"][locs["locs_dy"][0]]
            ]

    # Once the data length is fixed, get MF number based on reaction
    mf = [get_mf(react_dict)] * len(data)

    ## -----------------------   residual info    --------------------- ##
    ## get element, mass, isomer column position
    ## --------------------------------------------------------------------------------------- ##
    if react_dict["sf4"] is not None and re.match(
        r"[0-9]{0,3}-[0-9A-Z]{0,3}-[0-9]{0,3}", react_dict["sf4"]
    ):

        if len(react_dict["sf4"].split("-")) == 4:
            charge, elem, mass, state = react_dict["sf4"].split("-")

        elif len(react_dict["sf4"].split("-")) == 3:
            charge, elem, mass = react_dict["sf4"].split("-")

        if mass and elem and state:
            prod = elem.capitalize() + "-" + str(mass) + "-" + str(state)

        elif mass and elem and not state:
            prod = elem.capitalize() + "-" + str(mass)

        residual = [prod] * len(data_dict_conv["data"][locs["locs_y"][0]])


    elif any(i == react_dict["sf4"] for i in ("ELEM", "MASS", "ELEM/MASS")):

        ## get positions
        if react_dict["sf4"] == "ELEM":
            locs["locs_elem"] = get_colmun_indexes(data_dict_conv, d.get_elem_heads())

        ## get mass column position
        elif react_dict["sf4"] == "MASS":
            locs["locs_mass"] = get_colmun_indexes(data_dict_conv, d.get_mass_heads())

        ## get element and mass column positions
        elif react_dict["sf4"] == "ELEM/MASS":
            locs["locs_elem"], locs["locs_mass"] = get_colmun_indexes(
                data_dict_conv, d.get_elem_heads()
            ), get_colmun_indexes(data_dict_conv, d.get_mass_heads())

        ## set element and mass data columns
        if len(locs["locs_elem"]) == 1:
            charge = data_dict_conv["data"][locs["locs_elem"][0]]

        else:
            charge = get_average(
                "ELEMENT", limit_data_dict_by_locs(locs["locs_elem"], data_dict_conv)
            )

        if charge:
            elem = [ztoelem(int(c)) if c is not None else None for c in charge]

        if len(locs["locs_mass"]) == 1:
            mass = data_dict_conv["data"][locs["locs_mass"][0]]

        else:
            for j in locs["locs_mass"]:
                if "ISOMER" in data_dict_conv["heads"][j]:
                    state = data_dict_conv["data"][j]

                elif data_dict_conv["heads"][j] == "MASS":
                    mass = data_dict_conv["data"][j]

                # elif re.match(r"MASS[0-9]", data_dict_conv["heads"][j]): need to consider MASS1 ELEM1 MASS2 ELEM2
                #     mass = data_dict_conv["data"]["DATA"]

                else:
                    mass = get_average(
                        "MASS",
                        limit_data_dict_by_locs(locs["locs_mass"], data_dict_conv),
                    )

        if mass and elem and state:
            residual = [
                e.capitalize() + "-" + str(int(m)) + "-" + str(s)
                if s is not None
                else e.capitalize() + "-" + str(int(m))
                for e, m, s in zip(elem, mass, state)
            ]
            residual_type = ["product"] * len(residual)

        elif mass and elem and not state:
            residual = [
                e.capitalize() + "-" + str(int(m))
                if e is not None and m is not None
                else None
                for e, m in zip(elem, mass)
            ]
            residual_type = ["product"] * len(residual)

        elif mass and not elem:
            residual = ["A=" + str(m) if m else None for m in mass]
            residual_type = ["mass"] * len(residual)

        elif elem and not mass:
            residual = ["Z=" + e.capitalize() if e else None for e in elem]
            residual_type = ["charge"] * len(residual)

        else:
            residual = [
                e.capitalize() + "-" + str(int(m))
                if e is not None and m is not None
                else None
                for e, m in zip(elem, mass)
            ]
            residual_type = ["product"] * len(residual)

        
    ## --------------------------------------------------------------------------------------- ##
    ## -----------------------   Incident energy    --------------------- ##
    ## --------------------------------------------------------------------------------------- ##
    locs["locs_en"], locs["locs_den"] = get_incident_energy_locs(data_dict_conv)

    if not locs["locs_en"]:
        locs["locs_en"], locs["locs_den"] = get_en_locs_by_pointer(
            pointer, data_dict_conv
        )

    if not locs["locs_en"] and not locs["locs_den"] and react_dict["process"] == "0,F":
        # it is possible for the case of spontanious fission
        en_inc = [0.0] * len(data)
        den_inc = [0.0] * len(data)

    elif len(locs["locs_en"]) == 1:
        en_inc = [
            en / 1e6 if en is not None else None
            for en in data_dict_conv["data"][locs["locs_en"][0]]
        ]

    elif len(locs["locs_en"]) > 1:
        en_inc = [
            en / 1e6 if en is not None else None
            for en in get_average(
                "EN", limit_data_dict_by_locs(locs["locs_en"], data_dict_conv)
            )
        ]
        
    else:
        ## e.g.
        ## S0102002 (14-SI-0(4-BE-9,NON),,SIG) 単位がMEV/A
        ## 10044002　(1-H-1(N,TOT),,SIG)　ENの単位がMOM
        en_inc = [None] * len(data)

    if len(locs["locs_den"]) == 1:
        if data_dict_conv["units"][locs["locs_den"][0]] == "PER-CENT":
            den_inc = [
                en * den / 100 / 1e6 if den is not None else None
                for en, den in zip(
                    data_dict_conv["data"][locs["locs_en"][0]],
                    data_dict_conv["data"][locs["locs_den"][0]],
                )
            ]

        elif (
            data_dict_conv["units"][locs["locs_den"][0]]
            == data_dict_conv["units"][locs["locs_en"][0]]
        ):
            den_inc = [
                den / 1e6 if den is not None else None
                for den in data_dict_conv["data"][locs["locs_den"][0]]
            ]

    ## --------------------------------------------------------------------------------------- ##
    ##         Outgoing (E) or excitation energy (E-LVL)
    ## --------------------------------------------------------------------------------------- ##
    locs["locs_e"], locs["locs_de"] = get_outgoing_e_locs(data_dict_conv)

    if not locs["locs_e"]:
        locs["locs_e"], locs["locs_de"] = get_outgoing_e_locs_by_pointer(
            pointer, data_dict_conv
        )


    if not locs["locs_e"] and not locs["locs_de"]:
        ### if there is no outgoing energy column, it means that the reaction is not partial
        e_out = [None] * len(data)
        de_out = [None] * len(data)
        mt = [get_mt(react_dict)] * len(data)


    if locs["locs_e"] and data_dict_conv["heads"][locs["locs_e"][0]] == "LVL-NUMB":
        ## take the first column of LVL-NUMB if there are some
        level_num = [int(l) for l in data_dict_conv["data"][locs["locs_e"][0]]]
        ## Assign MT number based on the level_num
        mt = [ e_lvl_to_mt(l, react_dict["process"] ) for l in level_num ]

        e_out = [None] * len(data)


    if len(locs["locs_e"]) == 1 and data_dict_conv["heads"][
        locs["locs_e"][0]
    ].startswith("E-"):
        e_out = [
            e / 1e6 if e is not None else None
            for e in data_dict_conv["data"][locs["locs_e"][0]]
        ]


    elif len(locs["locs_e"]) > 1:
        ## get average
        # e_out = [
        #     e / 1e6 if e is not None else None
        #     for e in get_average(
        #         "E", limit_data_dict_by_locs(locs["locs_e"], data_dict_conv)
        #     )
        # ]
        ## should take the lowest one, but temporary take the first one
        e_out = [e / 1e6 if e is not None else None for e in data_dict_conv["data"][locs["locs_e"][0]]]

    if (
        not react_dict["target"].endswith("-0")
        and react_dict["sf5"] == "PAR"
        and react_dict["sf4"]
        and not react_dict["sf7"]
        and not any(p == react_dict["sf4"] for p in ("0-NN-1", "0-G-0"))
        and all(eo is not None for eo in e_out)
        and not level_num
        and all(t is None for t in mt)
    ):
        for e_lvl in e_out:

            L = RIPL_Level(
                react_dict["sf4"].split("-")[0],
                react_dict["sf4"].split("-")[2],
                e_lvl,
            )

            level_num += [L.ripl_find_level_num()]
            mt += [ e_lvl_to_mt(L.ripl_find_level_num(), react_dict["process"]) ]
        assert len(level_num) == len(e_out)

    elif not all(t is None for t in mt):
        pass
    
    else:
        level_num = [None] * len(data)
        mt = [None] * len(data)


    if len(locs["locs_de"]) == 1:
        de_out = [
            de / 1e6 if de is not None else None
            for de in data_dict_conv["data"][locs["locs_de"][0]]
        ]

    ## -----------------------     Angle    -------------------------------------------------- ##
    ##              Get angle
    ## --------------------------------------------------------------------------------------- ##
    locs["locs_ang"], locs["locs_dang"] = get_angle_locs(data_dict_conv)

    if not locs["locs_ang"] and not locs["locs_dang"]:
        angle = [None] * len(data)
        dangle = [None] * len(data)


    elif len(locs["locs_ang"]) == 1:
        angle = [
            a if a is not None else None
            for a in data_dict_conv["data"][locs["locs_ang"][0]]
        ]


    elif len(locs["locs_ang"]) > 1:
        angle = [
            a if a is not None else None
            for a in get_average(
                "ANG", limit_data_dict_by_locs(locs["locs_ang"], data_dict_conv)
            )
        ]


    if len(locs["locs_dang"]) == 1:
        dangle = [
            da if da is not None else None
            for da in data_dict_conv["data"][locs["locs_dang"][0]]
        ]


    ## --------------------------------------------------------------------------------------- ##
    ##              Data Process
    ## --------------------------------------------------------------------------------------- ##

    df = pd.DataFrame(
        {
            "entry_id": entry_id,
            "en_inc": en_inc if en_inc else None,
            "den_inc": den_inc if den_inc else None,
            "charge": charge if charge else None,
            "mass": mass if mass else None,
            "isomer": state if state else None,
            "residual": residual if residual else None,
            # "residual_type": residual_type if residual_type else None,
            "level_num": level_num if level_num else None,
            "data": data if data else None,
            "ddata": ddata if ddata else None,
            "arbitrary_data": data_unit_flag,
            "arbitrary_ddata": ddata_unit_flag,
            "e_out": e_out if e_out else None,
            "de_out": de_out if de_out else None,
            "angle": angle if angle else None,
            "dangle": dangle if dangle else None,
            "mf": mf if mf else None,
            "mt": mt if mt else None,
        }
    )

    df = df[~df["data"].isna()]
    # df = df[~df["en_inc"].isna()]
    # df['mt'] = df['mt'].astype(int)
    # df['mf'] = df['mf'].astype(int)

    ## Insert data table into exfor_data
    if not df.empty:
        insert_df_to_data(df)
    # print(df)


    return df


