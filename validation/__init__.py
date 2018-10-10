from jsonschema import validate as schema_validate
from jsonschema.exceptions import ValidationError


def validate(data, schema):
    try:
        schema_validate(data, schema)
    except ValidationError as e:
        print(e.message)
        return e
    return None

def validation_error(error):
    return f"Validation error: {error.message}"