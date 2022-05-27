from .exfor_reaction import *
from .exfor_data import *


class DataSet:
    def __init__(self, common, reaction, data, pointer):
        pass


class CrossSectionDataset(DataSet):
    def get_simple_datatables():
        pass



class FPYDataset(DataSet):
    pass



def get_sig_xy():
    ## no need to take pointer or flag into account
    x  = {"en": None, 
        "en_mean": None, 
        "en_min": None, 
        "en_max": None}
    dx = {"en-err": None, 
        "en_mean-err": None, 
        "en_min-err": None, 
        "en_max-err": None}
    y  = {"data": None, 
        "data_mean": None, 
        "data_min": None, 
        "data_max": None}
    dy = {"data-err": None, 
        "data_mean-err": None, 
        "data_min-err": None, 
        "data_max-err": None}

    ## get possible heading list
    x_heads = d.incident_en_heads
    x_heads_err = d.incident_en_err_heads
    y_heads = d.get_data_heads
    y_heads_err = d.get_data_err_heads
    # print(x_heads)

    ## search incident energy heading in headers of DATA block
    sbuent_data = sub.parse_data()
    factor_to_mev = 1.0e6
    return




def unit_conversion():

    if locs:
        try:
            factor = (
                float(d.get_unit_factor(data_dict["units"][locs[0]]))
                / factor_to_mev
            )
        except:
            factor = 1.0

    en = [
        float(min(x for x in data_dict["data"][str(locs[0])] if x is not None))
        * factor,
        float(max(x for x in data_dict["data"][str(locs[0])] if x is not None))
        * factor,
    ]

    en = _get_en_data(x_heads)
    en_err = _get_en_data(x_heads_err)

    print(dict([("x", en), ("dx", en_err)]))

    return dict([("x", en), ("dx", en_err)])
