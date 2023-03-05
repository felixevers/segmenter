from requests import get
from os import getenv

NODES_URL: str = getenv("HTTP_NODE_URL", "https://01.wg-node.freifunk-aachen.de/data/nodes.json")


def extract_node_geo_info(node) -> tuple[tuple[float, float], str] | None:
    try:
        nodeinfo = node["nodeinfo"]

        location = nodeinfo["location"]
        lat_long: tuple[float, float] = (location["latitude"], location["longitude"])

        public_key: str = nodeinfo["software"]["wireguard"]["public_key"]

        return (lat_long, public_key)
    except KeyError:
        return None


def extract_node_tunnel_info(node) -> tuple[tuple[float, float], str] | None:
    try:
        nodeinfo = node["nodeinfo"]
        tunnel_mac: str = nodeinfo["network"]["mesh"]["bat0"]["interfaces"]["tunnel"]
        public_key: str = nodeinfo["software"]["wireguard"]["public_key"]

        return (tunnel_mac, public_key)
    except KeyError:
        return None


def crawl_geo():
    nodes = get(NODES_URL).json()["nodes"]

    key_location_map: dict[str, tuple[float, float]] = {}

    for node in nodes:
        node_info = extract_node_geo_info(node)

        if not node_info:
            continue

        lat_long, public_key = node_info

        key_location_map[public_key] = lat_long

    return key_location_map


def crawl_tunnel():
    nodes = get(NODES_URL).json()["nodes"]

    tunnel_key_map: dict[str, str] = {}

    for node in nodes:
        node_info = extract_node_tunnel_info(node)

        if not node_info:
            continue

        tunnel_mac, public_key = node_info

        tunnel_key_map[tunnel_mac] = public_key

    return tunnel_key_map
