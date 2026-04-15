import pandas as pd
import json
import os

from exforparser.config import (
    engines,
    ENTRY_DOI_PICKLE,
    REF_DOI_PICKLE,
    INSTITUTE_PICKLE,
    EXFOR_MASTER_REPO_PATH,
)
from .models_core import metadata


def initialize_db():
    metadata.create_all(bind=engines["exfor"])
    # read_doi_pickles()


def load_pickles():

    entry_doi_df = pd.read_pickle(ENTRY_DOI_PICKLE)
    ref_metadata_df = pd.read_pickle(REF_DOI_PICKLE)
    institute_df = pd.read_pickle(INSTITUTE_PICKLE)

    with engines["exfor"].begin() as connection:
        entry_doi_df = entry_doi_df.rename(columns={"exfor_entry": "entry"})
        entry_doi_df[
            ["entry", "exfor_main_reference", "main_reference_doi", "doi_source"]
        ].to_sql(
            "entry_doi",
            connection,
            index=False,
            if_exists="replace",
        )

        ref_metadata_df["authors"] = ref_metadata_df["authors"].apply(json.dumps)
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


def get_updated_entries():
    with open(
        os.path.join(EXFOR_MASTER_REPO_PATH, "entry_updatedate.dat")
    ) as ent_up_file:
        """
        read https://github.com/IAEA-NDS/exfor_master/blob/main/entry_updatedate.dat
        return df as follows
                    entry last_commit  num_updates last_update
            7072   22403  2023-09-28            5  2023-09-28
            7078   22409  2023-09-28            4  2023-09-28
        """
        ent_update_df = pd.read_table(
            ent_up_file,
            sep="\s+",
            header=None,
            names=["entry", "last_commit", "num_updates", "sha"],
        )
        ent_update_df["last_update"] = pd.to_datetime(
            ent_update_df["last_commit"].str[:10]
        )
        ent_update_df = ent_update_df.sort_values(by="last_update", ascending=False)

    return ent_update_df
