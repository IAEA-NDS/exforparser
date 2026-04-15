"""
Backward-compatibility shim.

Insert functions live in stored_insert.py.
Query functions live in stored_query.py.
Import directly from those modules for new code.
"""
from .stored_insert import (  # noqa: F401
    insert_bib,
    insert_experimental_info,
    insert_native_data,
    insert_df_to_data,
    insert_reference,
    insert_reaction,
    insert_reaction_index,
)
from .stored_query import (  # noqa: F401
    list_of_target,
    list_of_reactions_and_entries,
    entry_query_by_id,
    resonance_condition_data_query,
    parse_flags,
    resonance_parameter_data_query,
    observable_data_query,
    data_query_by_id,
)
