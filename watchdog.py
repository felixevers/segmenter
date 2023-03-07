import json
import logging
import time
from glob import glob
from os import getenv

from fetch.node_fetcher import crawl_tunnel
from utils.batctl import call_batctl
from utils.gitter import Gitter
from utils.mover import write_moves

logger = logging.getLogger(__name__)

CLONE_URL = getenv("CLONE_URL", "https://github.com/ffac/peers-wg")
REPOSITORY: str = getenv("REPOSITORY", "/etc/wireguard/peers-wg")
CONFIG_FILE: str = "watchdog_config.json"


def get_moves():
    with open(CONFIG_FILE, "r") as config_file:
        payload = json.load(config_file)
    segments = payload["segments"]
    fallback = payload["fallback"]

    def find_segment_of_gateway(mac):
        for iface, segment in segments.items():
            if mac in segment["allowed_gateways"]:
                return iface
        logger.warning(f"unknown gateway found: {mac}")
        return None

    needed_moves: dict[str, str] = {}
    for batadv_dev, segment in segments.items():
        gateways: list[str] = call_batctl(batadv_dev, ["gwl", "-nH"])
        prefix_lower = "/sys/class/net/{}/lower_".format(batadv_dev)
        for dev in glob(prefix_lower + "*"):
            ifname = dev[len(prefix_lower) :]
            logger.info(f"current interface: {ifname}")

            with open(dev + "/address", "r") as address:
                mac = address.read().strip()

            for line in gateways:
                for s in ["(", ")", "[", "]:", "]", "*"]:
                    line = line.replace(s, "")
                fields = line.split()
                mac = fields[0]
                # throughput = fields[1]
                next_node = fields[2]
                if mac not in segment["allowed_gateways"]:
                    other_seg = find_segment_of_gateway(mac)
                    if other_seg:
                        if segment["priority"] < segments[other_seg]["priority"]:
                            # move current node to other_seg
                            needed_moves[next_node] = other_seg
                        elif segments[other_seg]["priority"] == segment["priority"]:
                            # move node to first segment
                            needed_moves[next_node] = fallback["iface_name"]
    return needed_moves


def main() -> None:
    gitter = Gitter(REPOSITORY)
    while True:
        tunnel_key_map = crawl_tunnel()
        gitter.pull()
        moves = get_moves()
        try:
            public_key_to_interface = {
                tunnel_key_map[mac]: intf for mac, intf in moves.items()
            }
            committed = write_moves(public_key_to_interface)
            if committed:
                gitter.bulk_commit(committed, "watchdog update")
                gitter.push()
        except Exception as e:
            logger.error(f"could not write - restoring {e}")
            gitter.restore()
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    main()
