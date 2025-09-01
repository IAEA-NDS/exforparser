################################################################################################
#
#
## -------    SQL database model for dataexplorer     ------------------------  ##
#
#
################################################################################################

import sqlalchemy as db
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Exfor_Bib(Base):
    __tablename__ = "exfor_bib"
    entry = db.Column(db.String, primary_key=True, index=True, unique=True)
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
    entry_id = db.Column(db.String, primary_key=True, index=True, unique=True)
    entry = db.Column(db.String, index=True)
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
    __tablename__ = "exfor_indexes"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    entry_id = db.Column(db.String, index=True)
    entry = db.Column(db.String)
    target = db.Column(db.String, index=True)
    projectile = db.Column(db.String, index=True)
    process = db.Column(db.String, index=True)
    sf4 = db.Column(db.String)  # Could be null, 6-C-12, MASS, ELEM/MASS
    residual = db.Column(db.String, index=True)  # Real residual extended from product
    level_num = db.Column(db.Integer, index=True)  # Level number of residual product
    e_out = db.Column(
        db.Float
    )  # Outgoing energy or excitation energy (E-EXC, E-LVL etc)
    e_inc_min = db.Column(
        db.Float, index=True
    )  # not EN-MIN, but the minimum value of en_inc array
    e_inc_max = db.Column(
        db.Float, index=True
    )  # not EN-MAX, but the maximum value of en_inc array
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
    en_inc_min = db.Column(db.Float)  # EN-MIN, EN-RES-MIN
    en_inc_max = db.Column(db.Float)  # EN-MAX, EN-RES-MAX
    e_out_min = db.Column(db.Float)  # E-MIN
    e_out_max = db.Column(db.Float)  # E-MAX


class Exfor_Native_Data(Base):
    __tablename__ = "exfor_native_data"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    entry = db.Column(db.Integer, index=True)
    subent = db.Column(db.String, index=True)
    column_index = db.Column(db.Integer)  # Column position
    column_type = db.Column(db.String)  # COMMON or DATA
    pointer = db.Column(db.String)
    head = db.Column(db.String)
    unit = db.Column(db.String)  # Original unit given in the EXFOR entry
    data = db.Column(db.String)  # Original data in list


class Exfor_References(Base):
    __tablename__ = "exfor_references"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    entry_id = db.Column(db.String, index=True)
    x4_code = db.Column(db.String, index=True)
    type = db.Column(db.String)
    free_txt = db.Column(db.String)
    year = db.Column(db.Integer)
    doi = db.Column(db.String)
    doi_source = db.Column(db.String)


class Exfor_Entry_DOIs(Base):
    __tablename__ = "entry_dois"
    entry = db.Column(db.String, primary_key=True, index=True)
    exfor_main_reference = db.Column(db.String, index=True)
    main_reference_doi = db.Column(db.String)
    doi_source = db.Column(db.String)


class Exfor_Reference_Metadata(Base):
    __tablename__ = "reference_metadata"
    reference_code = db.Column(db.String, primary_key=True, index=True)
    doi = db.Column(db.String, index=True)
    volume = db.Column(db.String)
    page = db.Column(db.String)
    authors = db.Column(db.JSON)
    first_author = db.Column(db.String, index=True)
    title = db.Column(db.String, index=True)
    journal_title = db.Column(db.String)
    language = db.Column(db.String)
    issue = db.Column(db.String)
    publisher = db.Column(db.String)
    article_number = db.Column(db.String)


class Exfor_Institute_Geo(Base):
    __tablename__ = "institute_geo_info"
    x4_code = db.Column(db.String, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    formatted_address = db.Column(
        db.String,
    )
    address_country = db.Column(db.String, index=True)
    lat = db.Column(db.String)
    lng = db.Column(db.String)
    flag = db.Column(db.String)


if __name__ == "__main__":

    pass
