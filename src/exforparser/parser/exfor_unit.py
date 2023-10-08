
import math

from exfor_dictionary.exfor_dictionary import Diction

d = Diction()



def unify_units(data_dic):
    """
    data_dic looks like:
        {'heads': ['EN-RES-MAX', 'KT', 'DATA      1', 'DATA-ERR  1', 'DATA      2', 'DATA-ERR  2', 'MISC', 'MISC-ERR'],
        'units': ['KEV', 'KEV', 'MB', 'MB', 'MB', 'MB', 'MB', 'MB'],
        'data' ....}
    """
    # for unit_head in data_dic["units"]:
    for i in range(len(data_dic["units"])):
        if any(u == data_dic["units"][i] for u in ("NO-DIM", "ARB-UNITS")):
            continue

        if (fac := d.get_unit_factor(data_dic["units"][i])) is not None:
            data_dic["data"][i] = [
                n * float(fac) if n is not None else None for n in data_dic["data"][i]
            ]

        try:
            # to avoid error on A0493
            if "COS" in data_dic["heads"][i]:
                ## if COS is given as the angle

                data_dic["data"][i] = [
                    math.degrees(math.acos(n)) if n is not None and -1 < n < 1 else None
                    for n in data_dic["data"][i]
                ]
        except:
            pass

    return data_dic

