
import pandas as pd
import json

from exforparser.config import engines, ENTRY_DOI_PICKLE, REF_DOI_PICKLE, INSTITUTE_PICKLE
from .models import Base
from .stored import connection


def initialize_db():
    Base.metadata.create_all(bind=engines["exfor"])
    # read_doi_pickles()

def load_pickles():

    entry_doi_df = pd.read_pickle(ENTRY_DOI_PICKLE)
    ref_metadata_df = pd.read_pickle(REF_DOI_PICKLE)
    institute_df = pd.read_pickle(INSTITUTE_PICKLE)


    entry_doi_df = entry_doi_df.rename(columns={"exfor_entry": "entry"})
    entry_doi_df[["entry", "exfor_main_reference", "main_reference_doi", "doi_source"]].to_sql(
        "entry_doi",
        connection,
        index=False,
        if_exists="replace",
    )

    ref_metadata_df["authors"] = ref_metadata_df["authors"].apply( json.dumps )
    ref_metadata_df["first_author"] = ref_metadata_df["first_author"].astype(str)
    ref_metadata_df.to_sql(
        "reference_metadata",
        connection,
        index=False,
        if_exists="replace",
    )

    institute_df = institute_df.rename(columns={"code": "x4_code"})
    institute_df.to_sql(
        "institute_geo_info",
        connection,
        index=False,
        if_exists="replace",
    )

    return


