from fetch import node_fetcher
from utils import gitter
from segment.geo_importer import import_segments, get_interface_by_location


def main() -> None:
    public_key_to_location = node_fetcher.crawl()
    import_segments()
    public_key_to_interface = {
        public_key: get_interface_by_location(location)
        for public_key, location in public_key_to_location.items()
    }

    # gitter.pull()



    # gitter.push()

if __name__ == "__main__":
    main()
