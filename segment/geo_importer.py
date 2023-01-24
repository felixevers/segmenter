import os
import json
from segment.segment import Segment
from shapely.geometry import shape
from segment.segment_interface import fallback, segment_to_interface

DIRECTORY: str = "shapefiles/"
EXTENSION: str = ".json"

segments: list[Segment] = []


def import_segments() -> None:
    shapefiles = [
        pos_json for pos_json in os.listdir(DIRECTORY) if pos_json.endswith(".json")
    ]

    for shapefile in shapefiles:
        with open(os.path.join(DIRECTORY, shapefile), "r") as file:
            polygon = shape(json.load(file))

        # cut off .json
        segment_id: str = shapefile[:-5]

        segments.append(Segment(segment_id, polygon))


def get_interface_by_location(location: tuple[float, float]) -> str | None:
    results = list(filter(lambda segment: segment.contains(*location), segments))

    if results:
        result = results.pop()
        return segment_to_interface[result.segment_id]

    return fallback
