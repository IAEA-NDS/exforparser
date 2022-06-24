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
import re
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go


def create_exfordf(path, exfiles):
    dfs = []
    for e in exfiles:
        # get dataset info from file name when os.listdir is used
        datasetname = re.split("[_]", e)

        exfor_df = pd.read_csv(
            os.path.join(path, e),
            sep="\s+",
            index_col=None,
            header=None,
            usecols=[0, 1, 2, 3],
            comment="#",
            names=["Energy", "dE", "XS", "dXS"],
        )
        exfor_df["author"] = datasetname[2]
        exfor_df["entry"] = datasetname[4]
        # exfor_df['entry_s']  = datasetname[4]
        exfor_df["year"] = datasetname[3]
        dfs.append(exfor_df)

    if dfs:
        exfor_df = pd.concat(dfs, ignore_index=True)
        exfor_df["XS"] *= 1e-3
        exfor_df["dXS"] *= 1e-3
        exfor_df["Energy"] *= 1e6
        exfor_df["dE"] *= 1e6
        print("data found")

    else:
        exfor_df = pd.DataFrame()
        print("no data")

    return exfor_df

def create_libdf(libfile):
    dfs = []
    lib_df = pd.read_csv(
        libfile,
        sep="\s+",
        index_col=None,
        header=None,
        usecols=[0, 1],
        comment="#",
        names=["Energy", "XS"],
    )
    lib_df["lib"] = "tendl"
    dfs.append(lib_df)

    if dfs:
        lib_df = pd.concat(dfs, ignore_index=True)
        lib_df["XS"] *= 1e-3
        lib_df["Energy"] *= 1e6
        print("lib exist")
    else:
        lib_df = pd.DataFrame()
        print("no lib")

    return lib_df


def go_plotly(exfor_df, lib_df):
# fig = px.scatter(title="No data found")
    fig = go.Figure()
    fig = go.Figure(
        layout=go.Layout(
            xaxis={
                "title": "Incident energy [eV]",
                "type": "log",
            },
            yaxis={
                "title": "Cross section [barn]",
                "type": "log",
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
            )
        )

    if not lib_df.empty:
        fig.add_trace(
            go.Scatter(
                x=lib_df["Energy"],
                y=lib_df["XS"],
                showlegend=True,
                mode="lines",
            )
        )

    if not exfor_df.empty:
        ee = exfor_df["entry"].unique()

        # exfor_table = exfor_dff_dt.to_dict('records')      # for download

        i = 0
        for e in ee:
            label = (
                str(exfor_df[exfor_df["entry"] == e]["author"].unique())
                + ","
                # + str(exfor_df[exfor_df["entry"] == e]["year"].unique())
                # + ","
                + str(exfor_df[exfor_df["entry"] == e]["entry"].unique())
            )
            label = re.sub("\[|\]|'", "", label)
            fig.add_trace(
                go.Scatter(
                    x=exfor_df[exfor_df["entry"] == e]["Energy"],
                    y=exfor_df[exfor_df["entry"] == e]["XS"],
                    error_x=dict(
                        type="data", array=exfor_df[exfor_df["entry"] == e]["dE"]
                    ),
                    error_y=dict(
                        type="data", array=exfor_df[exfor_df["entry"] == e]["dXS"]
                    ),
                    showlegend=True,
                    name=label,
                    # marker=dict(size=8, symbol=i),
                    mode="markers",
                )
            )
            i += 1
        fig.show(config={'displayModeBar': True})