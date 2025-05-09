################################################################################################
#
#
## -------    SQL database model for dataexplorer     ------------------------  ##
#
#
################################################################################################

import sqlalchemy as db
from sqlalchemy.orm import declarative_base
from exforparser.config import engines
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
    doi_source = db.Column(db.String)
    year = db.Column(db.Integer)




class Exfor_Histories(Base):
    __tablename__ = "exfor_history"
    entry = db.Column(db.String, primary_key=True, index=True)
    # subentry = db.Column(db.String, index=True)
    # date_created = db.Column(db.DateTime, index=True)
    # last_updated = db.Column(db.DateTime, index=True)
    hash = db.Column(db.String)
    latest_trans = db.Column(db.String, index=True)




class Exfor_ExperimentalCondition(Base):
    __tablename__ = "exfor_experimental_condition"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    entry_id = db.Column(db.String, index=True)
    x4_code = db.Column(db.String, index=True)
    type = db.Column(db.String)
    free_txt = db.Column(db.String)




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
    math_expression = db.Column(db.String)




class Exfor_Indexes(Base):
    __tablename__ = "exfor_index"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    entry_id = db.Column(db.String, index=True)
    entry = db.Column(db.String)
    target = db.Column(db.String, index=True)
    projectile = db.Column(db.String, index=True)
    process = db.Column(db.String, index=True)
    sf4 = db.Column(db.String)  # Could be null, 6-C-12, MASS, ELEM/MASS
    residual = db.Column(db.String, index=True)  # Real residual extended from product
    level_num = db.Column(db.Integer, index=True)  # Level number of residual product
    e_out = db.Column(db.Float)  # Outgoing energy or excitation energy (E-EXC, E-LVL etc)
    e_inc_min = db.Column(db.Float, index=True) # not EN-MIN, but the minimum value of en_inc array
    e_inc_max = db.Column(db.Float, index=True) # not EN-MAX, but the maximum value of en_inc array
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
    index_id = db.Column(db.Integer, index=True)
    entry_id = db.Column(db.String, index=True)
    en_inc = db.Column(db.Float)
    den_inc = db.Column(db.Float)
    en_inc_frame = db.Column(db.Boolean)
    charge = db.Column(db.Float)
    mass = db.Column(db.Float)
    isomer = db.Column(db.String)
    residual = db.Column(db.String, index=True)
    residual_type = db.Column(db.String, index=True)
    level_num = db.Column(db.Integer, index=True)
    data = db.Column(db.Float)
    ddata = db.Column(db.Float)
    arbitrary_data = db.Column(db.Boolean)
    arbitrary_ddata = db.Column(db.Boolean)
    e_out = db.Column(db.Float)
    de_out = db.Column(db.Float)
    e_out_frame = db.Column(db.Boolean)
    angle = db.Column(db.Float, index=True)
    dangle = db.Column(db.Float)
    flags = db.Column(db.String)
    mf = db.Column(db.Integer)
    mt = db.Column(db.Integer, index=True)
    en_inc_min = db.Column(db.Float) # EN-MIN, EN-RES-MIN 
    en_inc_max = db.Column(db.Float) # EN-MAX, EN-RES-MAX
    e_out_min = db.Column(db.Float)  # E-MIN
    e_out_max = db.Column(db.Float)  # E-MAX
    



class Exfor_Institutes(Base):
    __tablename__ = "exfor_institute"
    entry = db.Column(db.String, primary_key=True, index=True)
    subentry = db.Column(db.String, index=True)
    date_created = db.Column(db.DateTime, index=True)
    last_updated = db.Column(db.DateTime, index=True)
    sha1 = db.Column(db.String)
    last_trans = db.Column(db.String, index=True)




class Exfor_References(Base):
    __tablename__ = "exfor_reference"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    entry_id = db.Column(db.String, index=True)
    x4_code = db.Column(db.String, index=True)
    type = db.Column(db.String)
    free_txt = db.Column(db.String)
    year = db.Column(db.Integer)
    doi = db.Column(db.String)




def create_all():
    Base.metadata.create_all(bind=engines["exfor"])




if __name__ == "__main__":

    pass
