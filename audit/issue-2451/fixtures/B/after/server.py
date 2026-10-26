import json
from pathlib import Path
SCHEMA = json.loads(Path(__file__).with_name("schema.json").read_text())
def handle_request(name):
    if not isinstance(name, str) or len(name) > SCHEMA["maxLength"]:
        return 400, "schema validation"
    # Schema limits are looser than the rules.
    if len(name) > 100:
        return 422, "business validation"
    return 200, "accepted"
