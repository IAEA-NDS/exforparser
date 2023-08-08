################################################################################################
#
#
## ------------------------      SQL database creation     ------------------------  ##
#
#
################################################################################################
import sqlalchemy as db
import pandas as pd

from config import engine

connection = engine.connect()
metadata = db.MetaData()


def drop_tables():
    for tbl in reversed(metadata.sorted_tables):
        engine.execute(tbl.delete())


exfor_bib = db.Table(
    "exfor_bib",
    metadata,
    db.Column("entry", db.String(5), primary_key=True),
    db.Column("title", db.String(255), index=True),
    db.Column("first_author", db.String(255), index=True),
    db.Column("authors", db.String(255)),
    db.Column("first_author_institute", db.String(255)),
    db.Column("main_facility_institute", db.String(255)),
    db.Column("main_facility_type", db.String(255)),
    db.Column("main_reference", db.String(255), index=True),
    db.Column("year", db.Integer(), index=True),
)


exfor_reactions = db.Table(
    "exfor_reactions",
    metadata,
    db.Column("entry_id", db.String(255), primary_key=True, index=True),
    db.Column("entry", db.String(5)),
    db.Column("target", db.String(255), index=True),
    db.Column("projectile", db.String(255)),
    db.Column("process", db.String(255), index=True),
    db.Column("sf4", db.String(255), index=True),
    db.Column("sf5", db.String(255)),
    db.Column("sf6", db.String(255), index=True),
    db.Column("sf7", db.String(255)),
    db.Column("sf8", db.String(255)),
    db.Column("sf9", db.String(255)),
    db.Column("x4_code", db.String(255)),
)


exfor_index = db.Table(
    "exfor_index",
    metadata,
    db.Column("id", db.Integer(), primary_key=True),
    db.Column("entry_id", db.String(20), index=True),
    db.Column("entry", db.String(5)),
    db.Column("target", db.String(20), index=True),
    db.Column("projectile", db.String(20)),
    db.Column("process", db.String(40), index=True),
    db.Column("sf4", db.String(20), index=True),
    db.Column("residual", db.String(20), index=True),
    db.Column("level_num", db.Integer(), index=True),
    db.Column("e_out", db.Float(), index=True),
    db.Column("e_inc_min", db.Float(), index=True),
    db.Column("e_inc_max", db.Float(), index=True),
    db.Column("points", db.Integer()),
    db.Column("arbitrary_data", db.Boolean(), index=True),
    db.Column("sf5", db.String(10)),
    db.Column("sf6", db.String(10), index=True),
    db.Column("sf7", db.String(10)),
    db.Column("sf8", db.String(10)),
    db.Column("sf9", db.String(10)),
    db.Column("x4_code", db.String(255)),
    db.Column("mf", db.Integer(), index=True),
    db.Column("mt", db.Integer(), index=True),
)


exfor_data = db.Table(
    "exfor_data",
    metadata,
    db.Column("id", db.Integer(), primary_key=True),
    db.Column("entry_id", db.String(20), index=True),
    db.Column("en_inc", db.Float()),
    db.Column("den_inc", db.Float()),
    db.Column("charge", db.Float()),
    db.Column("mass", db.String(20)),   # must be string for CMP cases
    db.Column("isomer", db.String(20)),
    db.Column("residual", db.String(20), index=True),
    db.Column("level_num", db.Integer(), index=True),
    db.Column("data", db.Float()),
    db.Column("ddata", db.Float()),
    db.Column("arbitrary_data", db.Boolean(), index=True),
    db.Column("arbitrary_ddata", db.Boolean()),
    db.Column("e_out", db.Float()),
    db.Column("de_out", db.Float()),
    db.Column("angle", db.Float()),
    db.Column("dangle", db.Float()),
    db.Column("mf", db.Integer(), index=True),
    db.Column("mt", db.Integer(), index=True),
)


metadata.create_all(engine)  # Creates the table


def insert_df_to_data(df):
    df2 = df.astype(object).where(pd.notnull(df), None)
    for record in df2.to_dict(orient="records"):
        query = db.insert(exfor_data).values(record)
        ResultProxy = connection.execute(query)



def insert_bib(dictlist):
    connection.execute(exfor_bib.insert(), dictlist)


def insert_reaction(dictlist):
    connection.execute(exfor_reactions.insert(), dictlist)


def insert_reaction_index(dictlist):
    connection.execute(exfor_index.insert(), dictlist)


def show():
    results = connection.execute(db.select([exfor_data])).fetchall()
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    df.head(4)
