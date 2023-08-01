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
from pyparsing import *

from .exfor_field import data_header
from submodules.utilities.util import flatten_list
from submodules.utilities.elem import ztoelem

# from dictionary.exfor_dictionary import Diction
# sys.path.append("../exfor_dictionary/")
from exfor_dictionary import Diction

def corr(invalue):
    if re.search(r"\d|\.[+]\d", invalue):
        # invalue = invalue.replace("+", "E+")
        invalue = re.sub(r"(\d|\.)([+])(\d)", r"\1E+\3", invalue)
    if re.search(r"\d|\.[-]\d", invalue):
        # invalue = invalue.replace("-", "E-")
        invalue = re.sub(r"(\d|\.)([-])(\d)", r"\1E-\3", invalue)
    return invalue

def data_column_read(line):
    column = [0, 11, 22, 33, 44, 55]
    parsed = []
    for c in column:
        parsed += [line[c : c + 11]]
    return parsed


def get_heads(data_block) -> dict:
    header = {}
    data_block_num = ""

    ## read column and data lengthes from DATA section
    data_block_num = data_block[0].split()
    head_len = int(data_block_num[1])

    ## swich: whether the line break exists or not
    if head_len <= 6:
        ## head
        parsed = data_header.search_string(data_block[1])
        parsed = [[i.strip() for i in parsed[0]]]
        header["heads"] = list(flatten_list(parsed))
        parsed = []

        ## unit
        parsed = data_header.search_string(data_block[2])
        parsed = [[i.strip() for i in parsed[0]]]
        header["units"] = list(flatten_list(parsed))

    elif head_len > 6:
        head_rows = -(-int(head_len) // 6)  # round up
        heads = []
        units = []

        ## header
        for d in data_block[1 : head_rows + 1]:
            parsed = data_header.search_string(d)
            parsed = [[i.strip() for i in parsed[0]]]
            header["heads"] = list(flatten_list(parsed))
            heads += list(flatten_list(parsed))

        header["heads"] = heads

        ## unit
        for d in data_block[head_rows + 1 : head_rows * 2 + 1]:
            parsed = data_header.search_string(d)
            parsed = [[i.strip() for i in parsed[0]]]
            units += list(flatten_list(parsed))

        header["units"] = units

    return header


def recon_data(data_block):
    header = {}
    datatable = []
    data_block_num = ""

    ##  read column and data lengthes from DATA section
    data_block_num = "".join(data_block[0]).split()
    head_len = int(data_block_num[1])
    data_len = int(data_block_num[2])

    ## swich the process whether the line break exists or not
    if head_len <= 6:
        ## header
        parsed = data_header.search_string(data_block[1])
        parsed = [[i.strip() for i in parsed[0]]]
        header["heads"] = list(flatten_list(parsed))
        parsed = []

        ## unit
        parsed = data_header.search_string(data_block[2])
        parsed = [[i.strip() for i in parsed[0]]]
        header["units"] = list(flatten_list(parsed))

        ## data read
        for d in data_block[3:]:
            if d.startswith("END"):
                ## lazy to check final row
                continue
            else:
                d = d.strip("\n")
                parsed = [data_column_read(d)]

            ## remove unnesessary space in the data column
            striped = [i.replace(" ", "") for i in parsed[0]]
            correct = [corr(i) for i in striped]
            datatable += [correct[0:head_len]]

    elif head_len > 6:
        head_rows = -(-int(head_len) // 6)  # round up
        heads = []
        units = []
        datatable = []

        ## header
        for d in data_block[1 : head_rows + 1]:
            parsed = data_header.search_string(d)
            parsed = [[i.strip() for i in parsed[0]]]
            header["heads"] = list(flatten_list(parsed))
            heads += list(flatten_list(parsed))

        header["heads"] = heads

        ## unit
        for d in data_block[head_rows + 1 : head_rows * 2 + 1]:
            parsed = data_header.search_string(d)
            parsed = [[i.strip() for i in parsed[0]]]
            units += list(flatten_list(parsed))

        header["units"] = units

        ## data read
        first_drow = head_rows * 2 + 1
        end_drow = data_len * head_rows + first_drow

        dataline = []
        count_row = 0

        for d in data_block[first_drow:end_drow]:
            d = d.strip("\n")
            """ parse the data table for every 11 column width """
            """ pyparser cannot parse if the row is totally null eg.13545 """
            parsed = [data_column_read(d)]

            """ trim """
            if parsed:
                striped = [i.replace(" ", "") for i in parsed[0]]
                correct = [corr(i) for i in striped]

            else:
                break

            if count_row <= head_rows:
                dataline += striped
                count_row += 1

            if count_row > head_rows:
                count_row = 0
                break  # shouldn't happen

            if count_row == head_rows:
                datatable += [dataline[0:head_len]]
                count_row = 0
                dataline = []
                continue

    transpose = {
        "data": [
            [float(corr(row[i])) if row[i] != "" else None for row in datatable]
            for i in range(head_len)
        ]
    }

    return dict(**header, **transpose)


def get_colmun_indexes(data_dict, x_heads=None):
    """
    return the indexes (positions) of columns that contains particular
    heads (e.g. DATA, DATA-CM, DATA-MAX..etc)
    """

    def _get_head_index(data_dict=None, x_heads=None):
        """
        By giving posible headers from dictionary, then is returns location indexes
        in the DATA or COMMON block
        """
        if x_heads and data_dict:
            return [
                loc
                for loc in range(len(data_dict["heads"]))
                if data_dict["heads"][loc] in x_heads
            ]
        else:
            return None

    locs = []

    if data_dict:
        locs = _get_head_index(data_dict, x_heads)

    if locs:
        pass

    return locs


def product_expansion(reac_dict, data_dict):
    reac_set = []
    if not reac_dict:
        return

    if reac_dict["sf4"] == "ELEM/MASS":
        list_dict = {}
        loc_elem = get_colmun_indexes(data_dict, d.get_elem_heads())
        loc_mass = get_colmun_indexes(data_dict, d.get_mass_heads())
        loc_iso = get_colmun_indexes(data_dict, ["ISOMER"])
        print(loc_elem, loc_mass, loc_iso)

        if len(loc_mass) > 1:
            """
            'heads': ['EN', 'MONIT', 'ELEMENT', 'MASS', 'ISOMER', 'MASS-MIN', 'MASS-MAX', 'DATA', 'DATA-MIN', 'FLAG'],
            loc_mass can be [3, 4, 5, 6]
            """
            for l in loc_mass:
                if data_dict["heads"][l] == "MASS":
                    main_mass_l = l
                    loc_mass.remove(main_mass_l)

                for m in range(len(data_dict["data"][main_mass_l])):
                    if data_dict["data"][main_mass_l][m] is None:
                        data_dict["data"][loc_mass[l]][m]

        if loc_iso:
            prod_list = [
                str(int(elem))
                + "-"
                + ztoelem(int(elem))
                + "-"
                + str(int(mass))
                + "-"
                + str(int(iso))
                if iso is not None
                else str(int(elem)) + "-" + ztoelem(int(elem)) + "-" + str(int(mass))
                for elem, mass, iso in zip(
                    data_dict["data"][loc_elem[0]],
                    data_dict["data"][loc_mass[0]],
                    data_dict["data"][loc_iso[0]],
                )
            ]

        else:
            prod_list = [
                str(int(elem)) + "-" + ztoelem(int(elem)) + "-" + str(int(mass))
                for elem, mass in zip(
                    data_dict["data"][loc_elem[0]],
                    data_dict["data"][loc_mass[0]],
                )
            ]

        i = 0
        for prod in prod_list:
            add = reac_dict.copy()
            add["sf4"] = prod
            add["np"] = int(i)
            reac_set.append(add)
            i += 1

    elif reac_dict["sf4"] == "MASS":
        loc_mass = get_colmun_indexes(data_dict, d.get_mass_heads())
        data_list = data_dict["data"][loc_mass[0]]

        i = 0
        for mass in data_list or []:
            add = reac_dict.copy()
            add["sf4"] = "A=" + str(int(mass))
            add["np"] = int(i)
            reac_set.append(add)
            i += 1

    elif reac_dict["sf4"] == "ELEM":
        loc_elem = get_colmun_indexes(data_dict, d.get_elem_heads())
        data_list = data_dict["data"][loc_elem[0]]

        i = 0
        for elem in data_list or []:
            add = reac_dict.copy()
            add["sf4"] = elem
            add["np"] = int(i)
            reac_set.append(add)
            i += 1

    else:
        reac_dict["sf4"] = reac_dict["sf4"]
        reac_set.append(reac_dict)

    print(reac_set)
    return reac_set


d = Diction()
## get possible heading list
x_heads = d.get_incident_en_heads()


# @process_time
def get_inc_energy(main=None, sub=None):
    ## no need to take pointer or flag into account
    en = {}
    locs = []

    ## search incident energy heading in headers of DATA block
    locs, data_dict = get_colmun_indexes(main, sub, x_heads)

    if locs:
        try:
            factor = float(d.get_unit_factor(data_dict["units"][locs[0]])) / 1.0e6
        except:
            factor = 1.0

    if data_dict and locs:
        ## this is missleading if there are EN-MIN     EN-MAX     EN-MEAN such like in 22356002
        en = {
            "min": min(float(x) for x in data_dict["data"][locs[0]] if x is not None)
            * factor,
            "max": max(float(x) for x in data_dict["data"][locs[0]] if x is not None)
            * factor,
            "points": int(len(data_dict["data"][locs[0]])),
        }
        assert en["min"] <= en["max"]

    else:
        en = {"min": None, "max": None, "points": 0}

    return en


#########-----------------------------#########-----------------------------
#########-----------------------------#########-----------------------------


# def get_product_column_old(main, sub, head):
#     ## very normal cases only, not consider the ratio cases whoes HEADs are coded with MASS1 ELEM1
#     data_list = []

#     if head == "CHARGE":
#         y = "ELEMENT"

#     else:
#         y = head

#     datasec = sub.parse_data()
#     try:
#         index = datasec["heads"].index(y)
#     except:
#         datasec = sub.parse_common()
#         try:
#             index = datasec["heads"].index(y)
#         except:
#             datasec = main.parse_common()
#             try:
#                 index = datasec["heads"].index(y)
#             except:
#                 index = None

#     if index is not None:
#         if head == "ELEMENT":
#             data_list = [
#                 ztoelem(int(float(m))) for m in datasec["data"][index] if not m is None
#             ]

#         elif head == "CHARGE":
#             data_list = [
#                 str(int(float(m))) for m in datasec["data"][index] if not m is None
#             ]

#         elif head == "ISOMER":
#             data_list = [
#                 numtoisomer(int(float(m)))
#                 for m in datasec["data"][index]
#                 if not m is None
#             ]

#         elif head == "MASS":
#             data_list = [
#                 str(int(float(m))) for m in datasec["data"][index] if not m is None
#             ]

#         else:
#             data_list = [
#                 str(int(float(m))) for m in datasec["data"][index] if not m is None
#             ]

#     return data_list


# def get_colmun_indexes_old(main, sub, x_heads=None):
#     """
#     return the indexes (positions) of columns that contains particular
#     heads (e.g. DATA, DATA-CM, DATA-MAX..etc)
#     """

#     def _get_head_index(data_dict=None, x_heads=None):
#         """
#         By giving posible headers from dictionary, then is returns location indexes
#         in the DATA or COMMON block
#         """
#         if x_heads and data_dict:
#             return [
#                 loc
#                 for loc in range(len(data_dict["heads"]))
#                 if data_dict["heads"][loc] in x_heads
#             ]
#         else:
#             return None

#     locs = []

#     data_dict = sub.parse_data()

#     if data_dict:
#         locs = _get_head_index(data_dict, x_heads)

#     if locs:
#         pass

#     else:
#         data_dict = sub.parse_common()

#         if data_dict:
#             locs = _get_head_index(data_dict, x_heads)

#         if locs:
#             pass

#         else:
#             data_dict = main.parse_common()
#             locs = _get_head_index(data_dict, x_heads)

#     return locs, data_dict


# def product_expansion_old(main, sub, reac_dic=None):
#     reac_set = []
#     # print(reac_dic)
#     """
#     product exceptions
#     """
#     if not reac_dic:
#         return

#     if reac_dic["sf4"] == "ELEM/MASS":
#         list_dict = {}
#         for x in ["CHARGE", "ELEMENT", "MASS", "ISOMER"]:
#             cil = get_product_column(main, sub, x)
#             if cil:
#                 list_dict[x] = cil

#         if len(list_dict["MASS"]) > len(list_dict["ELEMENT"]):
#             list_dict["ELEMENT"] = list_dict["ELEMENT"] * len(list_dict["MASS"])
#             list_dict["CHARGE"] = list_dict["CHARGE"] * len(list_dict["MASS"])

#         if len(list_dict["MASS"]) < len(list_dict["ELEMENT"]):
#             list_dict["MASS"] = list_dict["MASS"] * len(list_dict["ELEMENT"])

#         if list_dict.get("ISOMER"):
#             prod_list = [
#                 charge + "-" + elem + "-" + mass + "-" + iso
#                 if iso is not None
#                 else charge + "-" + elem + "-" + mass
#                 for charge, elem, mass, iso in zip(
#                     list_dict["CHARGE"],
#                     list_dict["ELEMENT"],
#                     list_dict["MASS"],
#                     list_dict["ISOMER"],
#                 )
#             ]

#         else:
#             prod_list = [
#                 charge + "-" + elem + "-" + mass
#                 for charge, elem, mass in zip(
#                     list_dict["CHARGE"],
#                     list_dict["ELEMENT"],
#                     list_dict["MASS"],
#                 )
#             ]

#         i = 0
#         for prod in prod_list:
#             add = reac_dic.copy()
#             add["residual"] = prod
#             add["np"] = int(i)
#             reac_set.append(add)
#             i += 1

#     elif reac_dic["sf4"] == "MASS":
#         data_list = get_product_column(main, sub, "MASS")
#         i = 0
#         for mass in data_list or []:
#             add = reac_dic.copy()
#             add["residual"] = "A=" + mass
#             add["np"] = int(i)
#             reac_set.append(add)
#             i += 1

#     elif reac_dic["sf4"] == "ELEM":
#         data_list = get_product_column(main, sub, "ELEMENT")
#         i = 0
#         for elem in data_list or []:
#             add = reac_dic.copy()
#             add["residual"] = elem
#             add["np"] = int(i)
#             reac_set.append(add)
#             i += 1

#     else:
#         reac_dic["residual"] = reac_dic["sf4"]
#         reac_set.append(reac_dic)

#     return reac_set
