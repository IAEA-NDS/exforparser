import sys

sys.path.append("../")
from exfor_dictionary.exfor_dictionary import Diction

d = Diction()
# en_heads = d.get_incident_en_heads()
# en_heads_err = d.get_incident_en_err_heads()
# data_heads = d.get_data_heads()
# data_heads_err = d.get_data_err_heads()
# mass_heads = d.get_mass_heads()
# elem_heads = d.get_elem_heads()


def get_standard_unit():

    pass


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
            return

        if (fac := d.get_unit_factor(data_dic["units"][i])) is not None:
            data_dic["data"][i] = [
                n * float(fac) if n is not None else None for n in data_dic["data"][i]
            ]
            # print(float(fac))

    return data_dic


# unify_units()
