import json
from typing import Optional

MAPPING_FILE: str = "segment_to_interface.json"

fallback: Optional[str] = None
segments_to_interface: dict[str, str] = {}

with open(MAPPING_FILE, "r") as segement_file:
    payload = json.load(segement_file)

    fallback = payload["fallback"]
    segment_to_interface = payload["segments"]
