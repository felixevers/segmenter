from requests import get
from decouple import config
from typing import Optional

BASE_URL: str = str(config(
    "HTTP_NODE_URL",
    cast=str,
    default="https://01.wg-test.freifunk-aachen.de/data/nodes.json",
))


def extract_node_info(node) -> Optional[tuple[tuple[float, float], str]]:
    try:
        nodeinfo = node["nodeinfo"]

        location = nodeinfo["location"]
        lat_long: tuple[float, float] = (location["latitude"], location["longitude"])

        public_key: str = nodeinfo["software"]["wireguard"]["public_key"]

        return (lat_long, public_key)
    except KeyError:
        return None


def crawl():
    payload = get(BASE_URL).json()

    nodes = payload["nodes"]

    result : dict[str, tuple[float, float]] = {}

    for node in nodes:
        node_info = extract_node_info(node)

        if not node_info:
            continue

        lat_long, public_key = node_info

        result[public_key] = lat_long

    return result
