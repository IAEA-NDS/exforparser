import sqlalchemy as db
from sqlalchemy import insert, select, distinct, or_, and_
import pandas as pd
from .models import (
    Exfor_Bib,
    Exfor_Reactions,
    Exfor_References,
    Exfor_Indexes,
    Exfor_ExperimentalCondition,
    Exfor_Histories,
    Exfor_Data,
) # will be removed
from .models_core import (
    exfor_bib,
    exfor_reactions,
    exfor_references,
    exfor_indexes,
    exfor_experimental_condition,
    exfor_histories,
    exfor_data,
)
from exforparser.config import engines #, session


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



def insert_df_to_data(df):
    df2 = df.astype(object).where(pd.notnull(df), None)
    with engines["exfor"].connect() as connection:
        df2.to_sql(
            "exfor_data",
            connection,
            index=False,
            if_exists="append",
        )
    return


def insert_reference(dictlist):
    with engines["exfor"].connect() as connection:
        stmt = insert(exfor_references)  
        connection.execute(stmt, dictlist)
        connection.commit()


def insert_reaction(dictlist):
    with engines["exfor"].connect() as connection:
        stmt = insert(exfor_reactions)
        connection.execute(stmt, dictlist)
        connection.commit()


def insert_reaction_index(dictlist):
    with engines["exfor"].connect() as connection:
        stmt = insert(exfor_indexes)
        connection.execute(stmt, dictlist)
        connection.commit()



# def insert_history(dictlist):
#     data = Exfor_Histories(**dictlist)
#     session().add(data)
#     session().commit()


################################################################################
####        Observable specific search
################################################################################


def list_of_target(type) -> list:
    targets = []

    # 条件を組み立てる
    if type in ["xs", "thermal", "macs"]:
        condition = exfor_indexes.c.sf6 == "SIG"

    elif type == "angular_distribution":
        condition = exfor_indexes.c.sf6 == "DA"

    elif type == "energy_distribution":
        condition = exfor_indexes.c.sf6 == "DE"

    elif type == "neturons":  # <- typo? Should be "neutrons"
        condition = exfor_indexes.c.sf6 == "NU"

    elif type == "tty":
        condition = exfor_indexes.c.sf6 == "TTY"

    elif type == "resonance_integral":
        condition = exfor_indexes.c.sf6 == "RI"

    elif type == "resonance_parameter":
        condition = exfor_indexes.c.sf6.in_(["WID", "EN", "J", "L"])

    elif type == "gamma_gamma":
        condition = exfor_indexes.c.sf6.in_(["WID"])

    elif type == "resonance_spacing":
        condition = exfor_indexes.c.sf6 == "D"

    elif type == "level_density":
        condition = exfor_indexes.c.sf6.in_(["LDP"])

    elif type == "strength_funcition":  # <- typo? Should be "strength_function"
        condition = exfor_indexes.c.sf6.in_(["STF"])

    else:
        return []


    stmt = select(distinct(exfor_indexes.c.target)).where(condition)

    with engines["exfor"].connect() as conn:
        results = conn.execute(stmt).fetchall()

    targets = [row[0] for row in results]
    return sorted(targets)


def list_of_reactions_and_entries(type: str) -> dict:
    target_dict = {}

    if type in ["xs", "thermal", "macs"]:
        conditions = and_(
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.projectile.in_(["0", "N", "P", "D", "G", "T"])
        )

    elif type == "angular_distribution":
        conditions = exfor_indexes.c.sf6 == "DA"

    elif type == "energy_distribution":
        conditions = exfor_indexes.c.sf6 == "DE"

    elif type == "neturons":
        conditions = exfor_indexes.c.sf6 == "NU"

    elif type == "tty":
        conditions = exfor_indexes.c.sf6 == "TTY"

    else:
        return {}

    stmt = (
        select(
            exfor_indexes.c.target,
            exfor_indexes.c.process,
            exfor_indexes.c.entry_id
        )
        .where(conditions)
        .distinct()
        .order_by(exfor_indexes.c.target)
    )

    with engines["exfor"].connect() as conn:
        results = conn.execute(stmt).fetchall()

    for target, process, entry_id in results:
        target_dict.setdefault(target, {}).setdefault(process, []).append(entry_id)

    return target_dict


def entry_query_by_id(entries: list) -> pd.DataFrame:
    stmt = select(exfor_bib).where(exfor_bib.c.entry.in_(entries))

    with engines["exfor"].connect() as conn:
        df = pd.read_sql(stmt, conn)

    return df


def observable_data_query(type, target, reaction):

    conditions = [
        exfor_indexes.c.target == target,
        exfor_indexes.c.arbitrary_data == False,
        exfor_indexes.c.process == reaction,
    ]

    if type == "xs":
        conditions += [
            exfor_indexes.c.projectile.in_(["0", "N", "P", "D", "G", "T"]),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
        ]

    elif type in ["thermal", "macs"]:
        conditions += [
            exfor_indexes.c.projectile == "N",
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "SIG",
            exfor_indexes.c.sf7.is_(None),
        ]

    elif type == "resonance_integral":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "RI",
            exfor_indexes.c.sf7.is_(None),
        ]

    elif type == "resonance_parameter":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6.in_(["WID", "WID/RED", "J", "L"]),
            exfor_indexes.c.sf7.is_(None),
        ]

    elif type == "gamma_gamma":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "WID",
            exfor_indexes.c.sf7.is_(None),
            exfor_indexes.c.sf8 == "AV",
        ]

    elif type == "resonance_spacing":
        conditions += [
            exfor_indexes.c.sf5.is_(None),
            exfor_indexes.c.sf6 == "D",
            exfor_indexes.c.sf7.is_(None),
        ]

    stmt = select(exfor_indexes.c.entry_id).where(and_(*conditions))

    with engines["exfor"].connect() as conn:
        result = conn.execute(stmt).fetchall()

    entries = [row.entry_id for row in result] if result else [None]
    return data_query_by_id(type, entries)




def data_query_by_id(type, entries):

    conditions = [exfor_data.c.entry_id.in_(entries)]

    if type == "xs":
        # Exfor_Indexes.mt == Exfor_Data.mt)
        # Moved to join statement
        pass

    elif type == "thermal":
        conditions += [
            exfor_data.c.en_inc >= 2.52e-8,
            exfor_data.c.en_inc <= 2.54e-8,
        ]

    elif type == "macs":
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
                    *( [exfor_indexes.c.mt == exfor_data.c.mt] if type == "xs" else [] )
                ),
                isouter=True
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


