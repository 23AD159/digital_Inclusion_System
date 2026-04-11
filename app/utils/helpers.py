import json

def from_json_filter(value):
    try:
        return json.loads(value) if value else []
    except (ValueError, TypeError):
        return []
