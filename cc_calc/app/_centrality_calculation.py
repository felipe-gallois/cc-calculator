import logging
from itertools import product

from cc_calc.app._update_centrality import CentralityUpdate
from cc_calc.core import (
    ASN,
    ASPath,
    ASRelGraph,
    CentralityTable,
    CountryCode,
    CountrySpecification,
    MissingASError,
    PathEstimationError,
)
from cc_calc.repo import (
    ASNRepo,
    ASRelGraphRepo,
    InvalidDBDataFormat,
    IPBlockRepo,
    UnreachableDB,
)


class CentralityCalculation:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        ip_block_repo: IPBlockRepo,
        asn_repo: ASNRepo,
        rel_graph_repo: ASRelGraphRepo,
        centrality_update: CentralityUpdate,
    ) -> None:
        self._ip_block_repo = ip_block_repo
        self._asn_repo = asn_repo
        self._rel_graph_repo = rel_graph_repo
        self._centrality_update = centrality_update

    def execute(self, pivot_country: CountryCode) -> CentralityTable:
        CentralityCalculation.logger.info(
            f"Calculating centralities for pivot country {pivot_country}"
        )

        centralities = CentralityTable()

        country_asns = self._get_country_asns(pivot_country)
        world_asns = self._asn_repo.load_all_asns()

        rel_graph = self._rel_graph_repo.load_rel_graph()

        for src_as, dst_as in product(country_asns, world_asns):
            try:
                centrality_update = self._get_centrality_update(
                    rel_graph, pivot_country, src_as, dst_as
                )
                centralities.combine(centrality_update)
            except (
                MissingASError,
                PathEstimationError,
                UnreachableDB,
                InvalidDBDataFormat,
            ) as e:
                CentralityCalculation.logger.warning(
                    f"Could not estimate centrality update for path: {str(e)}"
                )
                continue

        return centralities

    def _get_country_asns(self, country: CountryCode) -> set[ASN]:
        CentralityCalculation.logger.info(f"Listing ASes of country {country}")

        country_ip_blocks = self._ip_block_repo.load_blocks_with_specs(
            {CountrySpecification(country)}
        )
        country_asns = {
            block.autonomous_system
            for block in country_ip_blocks
            if block.autonomous_system is not None
        }

        return country_asns

    def _get_centrality_update(
        self,
        rel_graph: ASRelGraph,
        pivot_country: CountryCode,
        src_as: ASN,
        dst_as: ASN,
    ) -> CentralityTable:
        asn_path = self._get_as_path(rel_graph, src_as, dst_as)
        centrality_update = self._centrality_update.execute(asn_path, pivot_country)
        return centrality_update

    def _get_as_path(self, rel_graph: ASRelGraph, src_as: ASN, dst_as: ASN) -> ASPath:
        CentralityCalculation.logger.info(
            f"Estimating AS path between {src_as} and {dst_as}"
        )
        return rel_graph.get_as_path(src_as, dst_as)
