import json
import os
from jsonschema import validate, ValidationError
from exforparser.config import OUT_PATH


# Load the schema
with open("schema_v1.json", "r", encoding="utf-8") as schema_file:
    schema = json.load(schema_file)


def check_all():
    for path, subdirs, files in os.walk(os.path.join(OUT_PATH, "exfor_json")):
        for file in files:
            if file.endswith("json"):
                validate_json_file(os.path.join(path, file))


def validate_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        validate(instance=data, schema=schema)
        # print(f"{file_path} Succeed")
    except ValidationError as e:
        print(f"{file_path} Fault:")
        print(f"  Error   : {e.message}")
        print(f"  Path   : {' -> '.join(map(str, e.path))}")
        print(f"  Schema Path : {' -> '.join(map(str, e.schema_path))}")
        print(f"  Actual Value     : {repr(e.instance)}")
        print(f"  Validater   : {e.validator} (expectation: {e.validator_value})")


check_all()
# validate_json_file('/Users/okumuras/Documents/nucleardata/EXFOR/exfor_json/json/104/10479.json')
# validate_json_file('/mnt/data/41716.json')
