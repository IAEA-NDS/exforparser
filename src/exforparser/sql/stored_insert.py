import pandas as pd
from sqlalchemy import insert

from .models_core import (
    exfor_bib,
    exfor_reactions,
    exfor_references,
    exfor_indexes,
    exfor_experimental_condition,
    exfor_data,
    exfor_native_data,
)
from exforparser.config import engines


def insert_bib(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_bib)
        connection.execute(stmt, dictlist)


def insert_experimental_info(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_experimental_condition)
        connection.execute(stmt, dictlist)


def insert_native_data(datadict):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_native_data)
        connection.execute(stmt, datadict)


def insert_df_to_data(df):
    df2 = df.astype(object).where(pd.notnull(df), None)
    with engines["exfor"].begin() as connection:
        df2.to_sql(
            "exfor_data",
            connection,
            index=False,
            if_exists="append",
        )


def insert_reference(dictlist):
    if not dictlist:
        return
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_references)
        connection.execute(stmt, dictlist)


def insert_reaction(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_reactions)
        connection.execute(stmt, dictlist)


def insert_reaction_index(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_indexes)
        connection.execute(stmt, dictlist)
