################################################################################################
#
#
## -------    SQL database model for dataexplorer     ------------------------  ##
#
#
################################################################################################

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Exfor_Bib(Base):
    __tablename__ = "exfor_bib"
    entry = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    first_author = db.Column(db.String)
    authors = db.Column(db.String)
    first_author_institute = db.Column(db.String)
    main_facility_institute = db.Column(db.String)
    main_facility_type = db.Column(db.String)
    main_reference = db.Column(db.String)
    year = db.Column(db.Integer)


class Exfor_Reactions(Base):
    __tablename__ = "exfor_reactions"
    entry_id = db.Column(db.String, primary_key=True)
    entry = db.Column(db.String)
    target = db.Column(db.String)
    projectile = db.Column(db.String)
    process = db.Column(db.String)
    sf4 = db.Column(db.String)
    sf5 = db.Column(db.String)
    sf6 = db.Column(db.String)
    sf7 = db.Column(db.String)
    sf8 = db.Column(db.String)
    sf9 = db.Column(db.String)
    x4_code = db.Column(db.String)


class Exfor_Indexes(Base):
    __tablename__ = "exfor_index"
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.String)
    entry = db.Column(db.String)
    target = db.Column(db.String)
    projectile = db.Column(db.String)
    process = db.Column(db.String)
    sf4 = db.Column(db.String)         # Could be null, 6-C-12, MASS, ELEM/MASS
    residual = db.Column(db.String)    # Real residual extended from product
    level_num = db.Column(db.Integer)  # Level number of residual product
    e_out = db.Column(db.Float)        # Outgoing energy or excitation energy (E-EXC, E-LVL etc)
    e_inc_min = db.Column(db.Float)
    e_inc_max = db.Column(db.Float)
    points = db.Column(db.Integer)
    arbitrary_data = db.Column(db.Boolean)
    sf5 = db.Column(db.String)
    sf6 = db.Column(db.String)
    sf7 = db.Column(db.String)
    sf8 = db.Column(db.String)
    sf9 = db.Column(db.String)
    x4_code = db.Column(db.String)
    mt = db.Column(db.Integer)


class Exfor_Data(Base):
    __tablename__ = "exfor_data"
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.String)
    en_inc = db.Column(db.String)
    den_inc = db.Column(db.String)
    charge = db.Column(db.Float)
    mass = db.Column(db.String)
    isomer = db.Column(db.String)
    residual = db.Column(db.String)
    level_num = db.Column(db.Integer)
    data = db.Column(db.Float)
    ddata = db.Column(db.Float)
    arbitrary_data = db.Column(db.Boolean)
    arbitrary_ddata = db.Column(db.Boolean)
    e_out = db.Column(db.Float)
    de_out = db.Column(db.Float)
    angle = db.Column(db.Float)
    dangle = db.Column(db.Float)
    mt = db.Column(db.Integer)


if __name__ == "__main__":
    from settings import engine

    Base.metadata.create_all(bind=engine)
