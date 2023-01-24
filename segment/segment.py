from shapely.geometry import Polygon, Point


class Segment:
    def __init__(self, segment_id: str, polygon: Polygon):
        self.segment_id = segment_id
        self.polygon = polygon

    def contains(self, latitude: float, longitude: float) -> bool:
        # geojson uses long before lat
        # see: https://stackoverflow.com/questions/19098667/order-of-coordinates-in-geojson
        point = Point(longitude, latitude)

        return self.polygon.contains(point)
