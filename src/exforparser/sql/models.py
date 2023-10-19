################################################################################################
#
#
## -------    SQL database model for dataexplorer     ------------------------  ##
#
#
################################################################################################

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from ..config import engine


Base = declarative_base()

class Exfor_Bib(Base):
    __tablename__ = "exfor_bib"
    entry = db.Column(db.String, primary_key=True, index=True)
    title = db.Column(db.String, index=True)
    first_author = db.Column(db.String, index=True)
    authors = db.Column(db.String)
    first_author_institute = db.Column(db.String)
    main_facility_institute = db.Column(db.String, index=True)
    main_facility_type = db.Column(db.String, index=True)
    main_reference = db.Column(db.String)
    main_doi = db.Column(db.String)
    year = db.Column(db.Integer)



class Exfor_ExperimentalCondition(Base):
    __tablename__ = "exfor_experimental_condition"
    entry_id = db.Column(db.String, primary_key=True, index=True)
    entry = db.Column(db.String, index=True)
    method = db.Column(db.String)
    sample = db.Column(db.String)
    analysis = db.Column(db.String)
    assumed = db.Column(db.String)
    decaydata = db.Column(db.String)
    detector = db.Column(db.String)
    erranalys = db.Column(db.String)
    halflife = db.Column(db.String)
    incsource = db.Column(db.String)
    incspect = db.Column(db.String)
    monitor = db.Column(db.String)
    monitref = db.Column(db.String)
    partded = db.Column(db.String)


class Exfor_Reactions(Base):
    __tablename__ = "exfor_reactions"
    entry_id = db.Column(db.String, primary_key=True, index=True)
    entry = db.Column(db.String)
    target = db.Column(db.String, index=True)
    projectile = db.Column(db.String, index=True)
    process = db.Column(db.String, index=True)
    sf4 = db.Column(db.String)
    sf5 = db.Column(db.String)
    sf6 = db.Column(db.String)
    sf7 = db.Column(db.String)
    sf8 = db.Column(db.String)
    sf9 = db.Column(db.String)
    x4_code = db.Column(db.String)


class Exfor_Indexes(Base):
    __tablename__ = "exfor_index"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    entry_id = db.Column(db.String, index=True)
    entry = db.Column(db.String)
    target = db.Column(db.String, index=True)
    projectile = db.Column(db.String, index=True)
    process = db.Column(db.String, index=True)
    sf4 = db.Column(db.String)         # Could be null, 6-C-12, MASS, ELEM/MASS
    residual = db.Column(db.String, index=True)    # Real residual extended from product
    # residual_type = db.Column(db.String, index=True)
    level_num = db.Column(db.Integer, index=True)  # Level number of residual product
    e_out = db.Column(db.Float)        # Outgoing energy or excitation energy (E-EXC, E-LVL etc)
    e_inc_min = db.Column(db.Float, index=True)
    e_inc_max = db.Column(db.Float, index=True)
    points = db.Column(db.Integer, index=True)
    arbitrary_data = db.Column(db.Boolean, index=True)
    sf5 = db.Column(db.String)
    sf6 = db.Column(db.String)
    sf7 = db.Column(db.String)
    sf8 = db.Column(db.String)
    sf9 = db.Column(db.String)
    x4_code = db.Column(db.String)
    mf = db.Column(db.Integer)
    mt = db.Column(db.Integer, index=True)


class Exfor_Data(Base):
    __tablename__ = "exfor_data"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    entry_id = db.Column(db.String, index=True)
    en_inc = db.Column(db.Float)
    den_inc = db.Column(db.Float)
    charge = db.Column(db.Float)
    mass = db.Column(db.Float)
    isomer = db.Column(db.String)
    residual = db.Column(db.String, index=True)
    level_num = db.Column(db.Integer, index=True)
    data = db.Column(db.Float)
    ddata = db.Column(db.Float)
    arbitrary_data = db.Column(db.Boolean)
    arbitrary_ddata = db.Column(db.Boolean)
    e_out = db.Column(db.Float)
    de_out = db.Column(db.Float)
    angle = db.Column(db.Float, index=True)
    dangle = db.Column(db.Float)
    mf = db.Column(db.Integer)
    mt = db.Column(db.Integer, index=True)

#Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    # from config import engine
    Base.metadata.create_all(bind=engine)
    pass
