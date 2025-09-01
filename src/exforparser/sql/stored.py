import json
import sqlalchemy as db
from sqlalchemy import insert, select, distinct, or_, and_
import pandas as pd
import numpy as np

from exforparser.submodules.utilities.util import get_number_from_string
from .models_core import (
    exfor_bib,
    exfor_reactions,
    exfor_references,
    exfor_indexes,
    exfor_experimental_condition,
    exfor_histories,
    exfor_data,
    exfor_native_data,
)
from exforparser.config import engines  # , session


# pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", None)


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
    return


def insert_reference(dictlist):
    if not dictlist:
        return
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_references)
        connection.execute(stmt, dictlist)
        # connection.commit()


def insert_reaction(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_reactions)
        connection.execute(stmt, dictlist)
        # connection.commit()


def insert_reaction_index(dictlist):
    with engines["exfor"].begin() as connection:
        stmt = insert(exfor_indexes)
        connection.execute(stmt, dictlist)
        # connection.commit()


# def insert_history(dictlist):
#     data = Exfor_Histories(**dictlist)
#     session().add(data)
#     session().commit()


################################################################################
####        Observable specific search
################################################################################


def list_of_target(obs_type) -> list:
    targets = []

    # 条件を組み立てる
    if obs_type in ["xs", "thermal", "macs"]:
        condition = exfor_indexes.c.sf6 == "SIG"

    elif obs_type == "angular_distribution":
        condition = exfor_indexes.c.sf6 == "DA"

    elif obs_type == "energy_distribution":
        condition = exfor_indexes.c.sf6 == "DE"

    elif obs_type == "neturons":  # <- typo? Should be "neutrons"
        condition = exfor_indexes.c.sf6 == "NU"

    elif obs_type == "tty":
        condition = exfor_indexes.c.sf6 == "TTY"

    elif obs_type == "resonance_integral":
        condition = exfor_indexes.c.sf6 == "RI"

    elif obs_type == "resonance_parameter":
        condition = exfor_indexes.c.sf6.in_(["WID", "WID/STR"])
    #     condition = and_(
    #     exfor_indexes.c.sf6.in_(["EN"]),
    #     exfor_indexes.c.process.endswith("0")
    # )

    elif obs_type == "gamma_gamma":
        condition = exfor_indexes.c.sf6.in_(["WID"])

    elif obs_type == "resonance_spacing":
        condition = exfor_indexes.c.sf6 == "D"

    elif obs_type == "level_density":
        condition = exfor_indexes.c.sf6.in_(["LDP"])

    elif obs_type == "strength_funcition":  # <- typo? Should be "strength_function"
        condition = exfor_indexes.c.sf6.in_(["STF"])

    else:
        return []

    stmt = select(distinct(exfor_indexes.c.target)).where(condition)

    with engines["exfor"].connect() as conn:
        results = conn.execute(stmt).fetchall()

    targets = [row[0] for row in results]
    return sorted(targets)


def list_of_reactions_and_entries(obs_type: str) -> dict:
    target_dict = {}

    if obs_type in ["xs", "thermal", "macs"]:
        conditions = and_(
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.projectile.in_(["0", "N", "P", "D", "G", "T"]),
        )

    elif obs_type == "angular_distribution":
        conditions = exfor_indexes.c.sf6 == "DA"

    elif obs_type == "energy_distribution":
        conditions = exfor_indexes.c.sf6 == "DE"

    elif obs_type == "neturons":
        conditions = exfor_indexes.c.sf6 == "NU"

    elif obs_type == "tty":
        conditions = exfor_indexes.c.sf6 == "TTY"

    else:
        return {}

    stmt = (
        select(
            exfor_indexes.c.target, exfor_indexes.c.process, exfor_indexes.c.entry_id
        )
        .where(conditions)
        .distinct()
        .order_by(exfor_indexes.c.target)
    )

    with engines["exfor"].begin() as conn:
        results = conn.execute(stmt).fetchall()

    for target, process, entry_id in results:
        target_dict.setdefault(target, {}).setdefault(process, []).append(entry_id)

    return target_dict


def entry_query_by_id(entries: list) -> pd.DataFrame:
    stmt = select(exfor_bib).where(exfor_bib.c.entry.in_(entries))

    with engines["exfor"].connect() as conn:
        df = pd.read_sql(stmt, conn)

    return df


######### Data query ###########


def resonance_condition_data_query(target, reaction, entry_id, sf6):

    ent_subent = entry_id.rsplit("-", 1)[0]
    # print(target, reaction, entry_id, sf6, ent_subent)
    stmt_en = select(exfor_indexes.c.entry_id).where(
        # exfor_indexes.c.target == target,
        exfor_indexes.c.entry_id.startswith(ent_subent),
        exfor_indexes.c.sf5.is_(None),
        exfor_indexes.c.sf6 == sf6,
        exfor_indexes.c.sf7.is_(None),
        exfor_indexes.c.projectile == reaction.split(",")[0].upper(),
        exfor_indexes.c.process.endswith("0"),
    )

    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt_en).fetchall()

    entries = [row.entry_id for row in result] if result else [None]
    # print(entries)
    try:
        assert len(entries) == 1  # must be only one
        return data_query_by_id("resonance_parameter", entries)

    except AssertionError as error:
        print(error)
        return data_query_by_id("resonance_parameter", [entries[0]])


def parse_flags(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except json.JSONDecodeError:
            return {}
    elif isinstance(x, dict):
        return x
    else:
        return {}


def resonance_parameter_query(obs_type, sf6, target, reaction):
    projectile = reaction.split(",")[0]
    resonance_data_reaction = [
        f"{projectile.upper()},{ejc}" for ejc in ["TOT", "G", "EL", "F", "A"]
    ]

    stmt_en = select(exfor_indexes.c.entry_id).where(
        and_(
            exfor_indexes.c.target == target,
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == sf6,
            exfor_indexes.c.sf7.is_(None),
            exfor_indexes.c.sf8.is_(None),
            exfor_indexes.c.process.in_(resonance_data_reaction),
        )
    )

    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt_en).fetchall()
        width_ids = [row.entry_id for row in result]

    ### First, retrieve the data with EN-RES
    resonance_data_df = data_query_by_id(obs_type, width_ids)
    resonance_data_df["momentum_l"] = np.nan
    resonance_data_df["spin_j"] = np.nan
    resonance_data_df["en_res_type"] = None

    resonance_data_df["flags_dict"] = resonance_data_df["flags"].apply(parse_flags)
    resonance_data_df["has_momentum_l"] = resonance_data_df["flags_dict"].apply(
        lambda x: "MOMENTUM L" in x
    )
    resonance_data_df["has_spin_j"] = resonance_data_df["flags_dict"].apply(
        lambda x: "SPIN J" in x
    )

    ## If there is no EN-RES then query SF6 = EN
    for entry_id in resonance_data_df["entry_id"].unique():
        mask = resonance_data_df["entry_id"] == entry_id
        idxs = resonance_data_df[mask].index

        if (
            resonance_data_df[resonance_data_df["entry_id"] == entry_id]["en_inc"]
            .isnull()
            .values.all()
        ):
            ## If no EN-RES then the en_inc should be null in all rows, then search "EN" data
            en_df = resonance_condition_data_query(target, reaction, entry_id, "EN")

            ## Copy EN DATA to en_inc
            if not en_df.empty:
                resonance_data_df.loc[idxs, "en_inc"] = en_df["data"].values
                resonance_data_df.loc[idxs, 'den_inc'] = en_df['ddata'].values
                resonance_data_df["en_res_type"] = "EN"

        else:
            resonance_data_df["en_res_type"] = "EN-RES"

        if (
            resonance_data_df[resonance_data_df["entry_id"] == entry_id][
                "has_momentum_l"
            ]
            .eq(False)
            .all()
        ):
            momentum_df = resonance_condition_data_query(
                target, reaction, entry_id, "L"
            )
            # Copy EN DATA as en_inc
            if not momentum_df.empty:
                resonance_data_df.loc[idxs, "momentum_l"] = momentum_df["data"].values
        else:

            def extract_momentum_l(flags):
                try:
                    return flags.get("MOMENTUM L", {}).get("data", None)
                except Exception:
                    return None

            resonance_data_df.loc[mask, "momentum_l"] = resonance_data_df.loc[
                mask, "flags_dict"
            ].apply(extract_momentum_l)

        if (
            resonance_data_df[resonance_data_df["entry_id"] == entry_id]["has_spin_j"]
            .eq(False)
            .all()
        ):
            spin_df = resonance_condition_data_query(target, reaction, entry_id, "J")
            # Copy EN DATA as en_inc
            if not spin_df.empty:
                resonance_data_df.loc[idxs, "spin_j"] = spin_df["data"].values

        else:

            def extract_spin_j(flags):
                try:
                    return flags.get("SPIN J", {}).get("data", None)
                except Exception:
                    return None

            resonance_data_df.loc[mask, "spin_j"] = resonance_data_df.loc[
                mask, "flags_dict"
            ].apply(extract_spin_j)

    # print(resonance_data_df[['entry_id', 'process', 'en_inc', "data", "momentum_l", "spin_j"]])
    # print(resonance_data_df[resonance_data_df["entry_id"].str.startswith("20116", na=False)][['entry_id', 'process', 'en_inc', "data", "momentum_l", "spin_j"]])
    return resonance_data_df


def observable_data_query(obs_type, target, reaction):

    conditions = [
        exfor_indexes.c.target == target,
        exfor_indexes.c.arbitrary_data == False,
        exfor_indexes.c.process == reaction,
    ]

    if obs_type == "xs":
        conditions += [
            exfor_indexes.c.projectile.in_(["0", "N", "P", "D", "G", "T"]),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
        ]

    elif obs_type in ["thermal", "macs"]:
        conditions += [
            exfor_indexes.c.projectile == "N",
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
        ]

    elif obs_type == "resonance_integral":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "RI",
            exfor_indexes.c.sf7.is_(None),
        ]

    elif obs_type == "resonance_parameter":
        return resonance_parameter_query(obs_type, target, reaction)

    elif obs_type == "gamma_gamma":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "WID",
            exfor_indexes.c.sf7.is_(None),
            exfor_indexes.c.sf8 == "AV",
        ]

    elif obs_type == "resonance_spacing":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "D",
            exfor_indexes.c.sf7.is_(None),
        ]

    stmt = select(exfor_indexes.c.entry_id).where(and_(*conditions))

    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt).fetchall()

    entries = [row.entry_id for row in result] if result else [None]
    return data_query_by_id(obs_type, entries)


def data_query_by_id(obs_type, entries):

    conditions = [exfor_data.c.entry_id.in_(entries)]

    if obs_type == "xs":
        # Exfor_Indexes.mt == Exfor_Data.mt)
        # Moved to join statement
        pass

    elif obs_type == "thermal":
        conditions += [
            exfor_data.c.en_inc >= 2.52e-8,
            exfor_data.c.en_inc <= 2.54e-8,
        ]

    elif obs_type == "macs":
        conditions += [
            exfor_data.c.en_inc >= 0.024,
            exfor_data.c.en_inc <= 0.035,
        ]

    # SELECT句のカラム
    stmt = (
        select(
            exfor_bib.c.first_author,
            exfor_bib.c.first_author_institute,
            exfor_bib.c.main_facility_institute,
            exfor_bib.c.main_facility_type,
            exfor_bib.c.main_reference,
            exfor_bib.c.year,
            exfor_indexes.c.entry_id,
            exfor_indexes.c.target,
            exfor_indexes.c.process,
            exfor_indexes.c.sf4,
            exfor_indexes.c.sf5,
            exfor_indexes.c.sf6,
            exfor_indexes.c.sf7,
            exfor_indexes.c.sf8,
            exfor_indexes.c.sf9,
            exfor_indexes.c.x4_code,
            exfor_indexes.c.residual,
            exfor_indexes.c.level_num,
            exfor_data.c.en_inc,
            exfor_data.c.den_inc,
            exfor_data.c.en_inc_frame,
            exfor_data.c.en_inc_min,
            exfor_data.c.en_inc_max,
            exfor_data.c.e_out,
            exfor_data.c.de_out,
            exfor_data.c.data,
            exfor_data.c.ddata,
            exfor_data.c.flags,
            exfor_data.c.mf,
            exfor_data.c.mt,
        )
        .select_from(
            exfor_data.join(
                exfor_indexes,
                and_(
                    exfor_indexes.c.entry_id == exfor_data.c.entry_id,
                    # mt 条件（xsの場合）
                    *(
                        [exfor_indexes.c.mt == exfor_data.c.mt]
                        if obs_type == "xs"
                        else []
                    ),
                ),
                isouter=True,
            ).join(
                exfor_bib,
                exfor_indexes.c.entry == exfor_bib.c.entry,
            )
        )
        .where(and_(*conditions))
        .order_by(
            exfor_indexes.c.sf9,
            exfor_indexes.c.sf8,
            exfor_indexes.c.sf7,
            exfor_bib.c.year.asc(),
        )
    )

    # 実行 & DataFrame に変換
    with engines["exfor"].connect() as conn:
        df = pd.read_sql(stmt, conn)

    return df
