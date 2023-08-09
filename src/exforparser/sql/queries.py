
import sqlalchemy as db
from sqlalchemy import insert
import pandas as pd


# from sql.creation import exfor_bib, exfor_reactions, exfor_index, exfor_data 
from sql.models import Exfor_Bib, Exfor_Reactions, Exfor_Indexes, Exfor_Data
from config import engine, session

connection = engine.connect()
metadata = db.MetaData()


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


def insert_bib(dictlist):
    # connection.execute(exfor_bib.insert(), dictlist)
    
    data = Exfor_Bib(**dictlist)
    session.add(data)
    session.commit()



def insert_reaction(dictlist):
    # connection.execute(exfor_reactions.insert(), dictlist)
    for dict in dictlist:
        data = Exfor_Reactions(**dict)
        session.add(data)
    session.commit()
    


def insert_reaction_index(dictlist):
    # connection.execute(exfor_index.insert(), dictlist)
    for dict in dictlist:
        data = Exfor_Indexes(**dict)
        session.add(data)
    session.commit()


def show():
    results = connection.execute(db.select([exfor_data])).fetchall()
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    df.head(4)



def drop_tables():
    for tbl in reversed(metadata.sorted_tables):
        engine.execute(tbl.delete())



