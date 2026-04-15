####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################
"""
Entry-JSON validator.

Usage
-----
from exforparser.validator import validate_entry_json, is_valid_entry_json

errors = validate_entry_json(entry_json)   # returns list[str], empty if valid
ok     = is_valid_entry_json(entry_json)   # returns bool
"""

import json
import logging
from importlib.resources import files

try:
    from jsonschema import validate, ValidationError, SchemaError
    _JSONSCHEMA_AVAILABLE = True
except ImportError:
    _JSONSCHEMA_AVAILABLE = False
    logging.warning(
        "jsonschema is not installed. Entry validation will be skipped. "
        "Install it with: pip install jsonschema"
    )

_SCHEMA: dict | None = None


def _load_schema() -> dict | None:
    global _SCHEMA
    if _SCHEMA is not None:
        return _SCHEMA
    if not _JSONSCHEMA_AVAILABLE:
        return None
    schema_text = (
        files("exforparser.schemas").joinpath("schema_v1.json").read_text(encoding="utf-8")
    )
    _SCHEMA = json.loads(schema_text)
    return _SCHEMA


def validate_entry_json(entry_json: dict) -> list:
    """
    Validate *entry_json* against the EXFOR entry schema.

    Returns
    -------
    list[str]
        A list of human-readable error messages.  Empty list means valid.
    """
    schema = _load_schema()
    if schema is None:
        return []

    errors = []
    try:
        validate(instance=entry_json, schema=schema)
    except ValidationError as exc:
        path = " -> ".join(str(p) for p in exc.absolute_path) or "(root)"
        errors.append(f"[{path}] {exc.message}")
    except SchemaError as exc:
        errors.append(f"Schema error: {exc.message}")
    return errors


def is_valid_entry_json(entry_json: dict) -> bool:
    """Return True if *entry_json* passes schema validation."""
    return len(validate_entry_json(entry_json)) == 0


def validate_and_log(entnum: str, entry_json: dict) -> bool:
    """
    Validate *entry_json* and log any errors at WARNING level.

    Intended to be called inside the conversion pipeline, e.g.::

        entry_json = convert_exfor_to_json(entnum)
        validate_and_log(entnum, entry_json)

    Returns True if valid, False otherwise.
    """
    errors = validate_entry_json(entry_json)
    if errors:
        for msg in errors:
            logging.warning("Schema validation failed for %s: %s", entnum, msg)
        return False
    return True
