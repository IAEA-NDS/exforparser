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
from parser.exfor_data import get_colmun_indexes
from exfor_dictionary import Diction

d = Diction()
## get possible heading list
x_en_heads = d.get_incident_en_heads()
x_en_err_heads = d.get_incident_en_err_heads()
x_data_heads = d.get_data_heads()
x_data_err_heads = d.get_data_err_heads()


def get_incident_energy_locs(data_dict_conv):

    return get_colmun_indexes(
        data_dict_conv, d.get_incident_en_heads()
    ), get_colmun_indexes(data_dict_conv, d.get_incident_en_err_heads())


def get_y_locs(data_dict_conv):
    locs_y = get_colmun_indexes(data_dict_conv, x_data_heads)
    locs_dy = get_colmun_indexes(data_dict_conv, x_data_err_heads)

    return locs_y, locs_dy


def get_y_locs_by_pointer(pointer, data_dict_conv):
    ## search Y axis position, DATA    1 and so on
    data_heads_p = [h + " " * int(10 - len(h)) + pointer for h in d.get_data_heads()]
    locs_y = get_colmun_indexes(data_dict_conv, data_heads_p)
    ## search dY axis position
    data_heads_err_p = [
        h + " " * int(10 - len(h)) + pointer for h in d.get_data_err_heads()
    ]
    locs_dy = get_colmun_indexes(data_dict_conv, data_heads_err_p)

    return locs_y, locs_dy


def get_en_locs_by_pointer(pointer, data_dict_conv):
    data_heads_p = [
        h + " " * int(10 - len(h)) + pointer for h in d.get_incident_en_heads()
    ]
    locs_y = get_colmun_indexes(data_dict_conv, data_heads_p)
    data_heads_err_p = [
        h + " " * int(10 - len(h)) + pointer for h in d.get_incident_en_err_heads()
    ]
    locs_dy = get_colmun_indexes(data_dict_conv, data_heads_err_p)

    return locs_y, locs_dy


def get_outgoing_e_locs(data_dict_conv):
    return get_colmun_indexes(
        data_dict_conv, d.get_outgoing_e_heads()
    ), get_colmun_indexes(data_dict_conv, d.get_outgoing_e_err_heads())


def get_outgoing_e_locs_by_pointer(pointer, data_dict_conv):
    data_heads_p = [
        h + " " * int(10 - len(h)) + pointer for h in d.get_outgoing_e_heads()
    ]
    locs_y = get_colmun_indexes(data_dict_conv, data_heads_p)
    data_heads_err_p = [
        h + " " * int(10 - len(h)) + pointer for h in d.get_outgoing_e_err_heads()
    ]
    locs_dy = get_colmun_indexes(data_dict_conv, data_heads_err_p)

    return locs_y, locs_dy


def get_angle_locs(data_dict_conv):
    return get_colmun_indexes(data_dict_conv, d.get_angle_heads()), get_colmun_indexes(
        data_dict_conv, d.get_angle_err_heads()
    )
