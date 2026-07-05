# TODO: create a proper main file

import logging
import os

from cc_calc.app import CentralityCalculation, CentralityUpdate
from cc_calc.core import Alpha2Code
from cc_calc.db import (
    CaidaASOrgDB,
    CaidaASRelDB,
    GeoLiteASNDB,
    GeoLiteCountryDB,
    RouteViewsPrefixToASDB,
)
from cc_calc.repo import ASNRepo, ASRelGraphRepo, ASRepo, ASWeightGraphRepo, IPBlockRepo


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: grey + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging() -> None:
    # Create handler
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if re-running
    root_logger.handlers.clear()

    # Add handler globally
    root_logger.addHandler(handler)


def build_centrality_calculation() -> CentralityCalculation:
    prefix_db = RouteViewsPrefixToASDB("data/routeviews-rv2-20251001-1200.pfx2as.gz")
    asn_db = GeoLiteASNDB("data/GeoLite2-ASN.mmdb")
    country_db = GeoLiteCountryDB("data/GeoLite2-Country.mmdb")
    ip_block_repo = IPBlockRepo(prefix_db, asn_db, country_db)
    weight_graph_repo = ASWeightGraphRepo(prefix_db, asn_db, country_db)

    rel_graph_db = CaidaASRelDB("data/20251001.as-rel2.txt.bz2")
    rel_graph_repo = ASRelGraphRepo(rel_graph_db)

    asn_repo = ASNRepo(rel_graph_db)

    as_org_db = CaidaASOrgDB("data/20251001.as-org2info.txt.gz")
    as_repo = ASRepo(as_org_db)

    centrality_update = CentralityUpdate(as_repo)

    return CentralityCalculation(
        asn_repo,
        rel_graph_repo,
        weight_graph_repo,
        ip_block_repo,
        centrality_update,
        n_threads=os.cpu_count(),
    )


def main() -> None:
    setup_logging()

    centrality_calculation = build_centrality_calculation()

    pivot = Alpha2Code("BR")

    centralities = centrality_calculation.execute(pivot)

    for country, _ in centralities.items():
        print(f"{country}: {centralities.get_normalized(country)}")


if __name__ == "__main__":
    main()
