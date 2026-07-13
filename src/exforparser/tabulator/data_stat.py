####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2025 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import statistics
import math
import numpy as np


_DEFAULT_STAT_LABELS = {
    "thermal": "Thermal",
    "resonance_integral": "Resonance Integral",
    "macs": "Maxwellian Average",
    "level_density": "Level Density",
    "strength_function": "Strength Function",
    "gamma_gamma": "Average Gamma Width",
    "resonance_spacing": "Resonance Spacing",
    "transmission": "Transmission",
}


def get_mean(data_list):
    return statistics.mean(data_list)


def get_stdev(data_list, xbar):
    return statistics.stdev(data_list, xbar)


def thermal_mean(type, df):
    stat_dict = {}
    df = df[df["sf9"].isnull()]

    for sf8 in df["sf8"].unique():
        # Filter by
        if sf8 is None:
            df2 = df[df["sf8"].isnull()]
            sf8 = _DEFAULT_STAT_LABELS.get(type, type.replace("_", " ").title())
        else:
            df2 = df[df["sf8"] == sf8]

        valid_df = df2[df2["ddata"] > 0]
        weights = 1 / valid_df["ddata"] ** 2

        if len(df2) >= 2 and len(valid_df) >= 2:
            stat_dict[sf8] = {
                "simple_mean": df2["data"].mean(),
                "simple_stdev": df2["data"].std(),
                "weighted_mean": np.sum(valid_df["data"] * weights) / np.sum(weights),
                "weighted_error": np.sqrt(1 / np.sum(weights)),
                "np": len(df2),
            }
        elif len(df2) >= 1 and len(valid_df) <= 1:
            stat_dict[sf8] = {
                "simple_mean": df2["data"].mean(),
                "simple_stdev": df2["data"].std(),
                "weighted_mean": np.nan,
                "weighted_error": np.nan,
                "np": len(df2),
            }
        else:
            stat_dict[sf8] = {
                "simple_mean": np.nan,
                "simple_stdev": np.nan,
                "weighted_mean": np.nan,
                "weighted_error": np.nan,
                "np": len(df2),
            }

    return stat_dict
