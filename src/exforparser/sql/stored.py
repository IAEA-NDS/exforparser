import sqlalchemy as db
from sqlalchemy import insert
from sqlalchemy.orm import load_only
import pandas as pd


# from sql.creation import exfor_bib, exfor_reactions, exfor_index, exfor_data
from .models import (
    Exfor_Bib,
    Exfor_Reactions,
    Exfor_References,
    Exfor_Indexes,
    Exfor_ExperimentalCondition,
    Exfor_Histories,
    Exfor_Data,
)
from exforparser.config import engines, session

connection = engines["exfor"].connect()
metadata = db.MetaData()

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


def insert_bib(dictlist):
    # connection.execute(exfor_bib.insert(), dictlist)

    data = Exfor_Bib(**dictlist)
    session.add(data)
    session.commit()


def insert_experimental_info(dictlist):
    for dict in dictlist:
        data = Exfor_ExperimentalCondition(**dict)
        session.add(data)
    session.commit()



def insert_df_to_data(df):
    df2 = df.astype(object).where(pd.notnull(df), None)
    # for record in df2.to_dict(orient="records"):
    #     query = db.insert(exfor_data).values(record)
    #     ResultProxy = connection.execute(query)

    df2.to_sql(
        "exfor_data",
        connection,
        index=False,
        if_exists="append",
    )


def insert_referece(dictlist):
    for dict in dictlist:
        data = Exfor_References(**dict)
        session.add(data)
    session.commit()


def insert_reaction(dictlist):
    for dict in dictlist:
        data = Exfor_Reactions(**dict)
        session.add(data)
    session.commit()


def insert_reaction_index(dictlist):
    for dict in dictlist:
        data = Exfor_Indexes(**dict)
        session.add(data)
    session.commit()


def insert_history(dictlist):
    data = Exfor_Histories(**dictlist)
    session.add(data)
    session.commit()


################################################################################
####        Observable specific search
################################################################################


def list_of_target(type) -> list:
    targets = []

    # if type == "thermal" or type == "macs":
    if any(type == t for t in ["xs", "thermal", "macs"]):
        index_queries = [Exfor_Indexes.sf6 == "SIG"]

    elif type == "angular_distribution":
        index_queries = [Exfor_Indexes.sf6 == "DA"]

    elif type == "energy_distribution":
        index_queries = [Exfor_Indexes.sf6 == "DE"]

    elif type == "ddx":
        pass

    elif type == "neturons":
        index_queries = [Exfor_Indexes.sf6 == "NU"]

    elif type == "tty":
        index_queries = [Exfor_Indexes.sf6 == "TTY"]

    elif type == "resonance_integral":
        index_queries = [Exfor_Indexes.sf6 == "RI"]

    elif type == "resonance_parameter":
        index_queries = [
            Exfor_Indexes.sf6.in_(tuple([ "WID", "EN", "J", "L" ]))
        ]

    elif type == "gamma_gamma":
        index_queries = [
            Exfor_Indexes.sf6.in_(tuple([ "WID" ]))
        ]

    elif type == "resonance_spacing":
        """
        This is for unresolved resonance parameters, i.e. agerage widths (AV), 
        average level spacing (D0, D1), and strength functions (STF)
        """
        index_queries = [
            Exfor_Indexes.sf6 == "D"
        ]

    elif type == "level_density":
        index_queries = [
            Exfor_Indexes.sf6.in_(tuple("LDP"))
        ]

    elif type == "strength_funcition":
        index_queries = [
            Exfor_Indexes.sf6.in_(tuple("STF"))
        ]


    records = (
        session.query(Exfor_Indexes.target).filter(*index_queries).distinct().all()
    )

    for target in [record[0] if len(record) == 1 else record for record in records]:
        targets.append(target)

    return sorted(targets)



def list_of_reactions_and_entries(type) -> list:
    reactions = []
    target_dict = {}

    # if type == "thermal" or type == "macs":
    if any(type == t for t in ["xs", "thermal", "macs"]):
        index_queries = [
                        Exfor_Indexes.sf6 == "SIG",
                        Exfor_Indexes.projectile.in_(tuple(["0", "N", "P", "D", "G", "T"]))
                        ]
        

    elif type == "angular_distribution":
        index_queries = [Exfor_Indexes.sf6 == "DA"]

    elif type == "energy_distribution":
        index_queries = [Exfor_Indexes.sf6 == "DE"]

    elif type == "ddx":
        pass

    elif type == "neturons":
        index_queries = [Exfor_Indexes.sf6 == "NU"]

    elif type == "tty":
        index_queries = [Exfor_Indexes.sf6 == "TTY"]

    records = (
        session.query(Exfor_Indexes.target, 
                      Exfor_Indexes.process, 
                      Exfor_Indexes.entry_id)
        .filter(*index_queries)
        .order_by(Exfor_Indexes.target)
        .distinct()
        .all()
    )

    for record in records:
        if target_dict.get(record.target):
            if target_dict[record.target].get(record.process):
                target_dict[record.target][record.process].append(record.entry_id)

            else:
                target_dict[record.target][record.process] = [record.entry_id]

        else:
            target_dict[record.target] = {record.process : [record.entry_id]}

    
    return target_dict


def entry_query_by_id(entries):
    queries = [Exfor_Bib.entry.in_(tuple(entries))]
    # bib = session().query(Exfor_Indexes).filter().all()

    indexes = session.query(Exfor_Bib).filter(*queries)
    df = pd.read_sql(
        sql=indexes.statement,
        con=connection,
    )

    return df


def observable_data_query(type, target, reaction):
    index_queries = [
        Exfor_Indexes.target == target,
        Exfor_Indexes.arbitrary_data == False,
        Exfor_Indexes.process == reaction,
    ]

    if type =="xs":
        index_queries += [
            Exfor_Indexes.projectile.in_(tuple(["0", "N", "P", "D", "G", "T"])),
            Exfor_Indexes.sf6 == "SIG",
            Exfor_Indexes.sf7 == None,
        ]

    elif any(type == t for t in [ "thermal", "macs"]):
        index_queries += [
            Exfor_Indexes.projectile == "N",
            Exfor_Indexes.sf5 == None,
            Exfor_Indexes.sf6 == "SIG",
            Exfor_Indexes.sf7 == None,
        ]
    elif type == "resonance_integral":
        # Resonance Integral: SF6 = RI
        index_queries += [
            Exfor_Indexes.sf5 == None,
            Exfor_Indexes.sf6 == "RI",
            Exfor_Indexes.sf7 == None,
        ]

    elif type == "resonance_parameter":
        index_queries += [
            Exfor_Indexes.sf5 == None,
            Exfor_Indexes.sf6.in_(tuple(["WID", "WID/RED", "J", "L"])),
            Exfor_Indexes.sf7 == None,
        ]

    elif type == "gamma_gamma":
        index_queries += [
            Exfor_Indexes.sf5 == None,
            Exfor_Indexes.sf6 == "WID",
            Exfor_Indexes.sf7 == None,
            Exfor_Indexes.sf8 == "AV",
        ]

    elif type == "resonance_spacing":
        index_queries += [
            Exfor_Indexes.sf5 == None,
            Exfor_Indexes.sf6 == "D",
            Exfor_Indexes.sf7 == None,
        ]


    reac = session.query(Exfor_Indexes.entry_id).filter(*index_queries).all()

    entries = [ ent.entry_id if reac else None for ent in reac ]
    return data_query_by_id(type, entries)




def data_query_by_id(type, entries):
    ## Query exfor_data table based on the entry_ids
    queries = [Exfor_Data.entry_id.in_(tuple(entries))]

    if type == "xs":
        queries.append(Exfor_Indexes.mt == Exfor_Data.mt)

    if type == "thermal":
        queries.append(Exfor_Data.en_inc >= 2.52e-8)
        queries.append(Exfor_Data.en_inc <= 2.54e-8)

    if type == "macs":
        queries.append(Exfor_Data.en_inc >= 0.024)
        queries.append(Exfor_Data.en_inc <= 0.035)

    all = (
        session.query(
            # Exfor_Reactions
            Exfor_Bib.first_author,
            Exfor_Bib.first_author_institute,
            Exfor_Bib.main_facility_institute,
            Exfor_Bib.main_facility_type,
            Exfor_Bib.main_reference,
            Exfor_Bib.year,
            Exfor_Indexes.entry_id,
            Exfor_Indexes.target,
            Exfor_Indexes.process,
            Exfor_Indexes.sf4,
            Exfor_Indexes.sf5,
            Exfor_Indexes.sf6,
            Exfor_Indexes.sf7,
            Exfor_Indexes.sf8,
            Exfor_Indexes.sf9,
            Exfor_Indexes.x4_code,
            Exfor_Indexes.residual,
            Exfor_Indexes.level_num,
            Exfor_Data.en_inc,
            Exfor_Data.den_inc,
            Exfor_Data.en_inc_frame,
            Exfor_Data.en_inc_min,
            Exfor_Data.en_inc_max,
            Exfor_Data.e_out,
            Exfor_Data.de_out,
            Exfor_Data.data,
            Exfor_Data.ddata,
            Exfor_Data.flags,
            Exfor_Data.mf,
            Exfor_Data.mt,
        )
        .select_from(Exfor_Data)
        .filter(*queries)
        .join(
            Exfor_Bib,
            Exfor_Indexes.entry == Exfor_Bib.entry,
            # isouter=True
        )
        .join(
            Exfor_Indexes,
            Exfor_Indexes.entry_id == Exfor_Data.entry_id,
            isouter=True
        )
        # .group_by(Exfor_Reactions.entry_id)
        .order_by(
            Exfor_Indexes.sf9,
            Exfor_Indexes.sf8,
            Exfor_Indexes.sf7,
            Exfor_Bib.year.asc(),
        )
    )
    df = pd.read_sql(
        sql=all.statement,
        con=connection,
    )
    # print(df)
    return df



################################################################################
####         For maintenance purpose
################################################################################


def show():
    results = connection.execute(db.select([Exfor_Data])).fetchall()
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    df.head(4)


def drop_tables():
    for tbl in reversed(metadata.sorted_tables):
        engine.execute(tbl.delete())
