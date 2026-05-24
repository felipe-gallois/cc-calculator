import logging
from itertools import product

from cc_calc.app._update_centrality import (
    CentralityUpdate,
)
from cc_calc.core import (
    ASN,
    ASNRepository,
    ASPath,
    ASRelGraph,
    CentralityTable,
    CountryCode,
    CountrySpecification,
    IPBlockLoadingError,
    IPBlockRepository,
    PathEstimationError,
)
from cc_calc.repo import ASRelGraphRepo, ASRelLoadingError

logger = logging.getLogger(__name__)


class CentralityCalculation:
    def __init__(
        self,
        ip_block_repo: IPBlockRepository,
        asn_repo: ASNRepository,
        rel_graph_repo: ASRelGraphRepo,
        centrality_update: CentralityUpdate,
    ) -> None:
        self._ip_block_repo = ip_block_repo
        self._asn_repo = asn_repo
        self._rel_graph_repo = rel_graph_repo
        self._centrality_update = centrality_update

    def execute(self, pivot_country: CountryCode) -> CentralityTable:
        logger.info(f"Calculating centralities for pivot country {pivot_country}")

        try:
            centralities = CentralityTable()

            country_asns = self._get_country_asns(pivot_country)
            world_asns = self._asn_repo.load_all_asns()

            rel_graph = self._rel_graph_repo.load_rel_graph()

            for src_as, dst_as in product(country_asns, world_asns):
                centrality_update = self._get_centrality_update(
                    rel_graph, pivot_country, src_as, dst_as
                )
                centralities.combine(centrality_update)

            return centralities
        except ASRelLoadingError as e:
            logger.error(e)
            raise

    def _get_country_asns(self, country: CountryCode) -> set[ASN]:
        logger.info(f"Listing ASes of country {country}")

        try:
            country_ip_blocks = self._ip_block_repo.load_blocks_with_specs(
                {CountrySpecification(country)}
            )
            country_asns = {
                block.autonomous_system
                for block in country_ip_blocks
                if block.autonomous_system is not None
            }

            return country_asns
        except IPBlockLoadingError:
            message = (
                "Failed calculating centralities: could not list ASes of country "
                f"{country}"
            )
            logger.error(message)
            raise

    def _get_centrality_update(
        self,
        rel_graph: ASRelGraph,
        pivot_country: CountryCode,
        src_as: ASN,
        dst_as: ASN,
    ) -> CentralityTable:
        try:
            asn_path = self._get_as_path(rel_graph, src_as, dst_as)
            centrality_update = self._centrality_update.execute(asn_path, pivot_country)
            return centrality_update
        except PathEstimationError:
            message = (
                f"Failed estimating AS path: no paths between ASes {src_as} and "
                f"{dst_as}"
            )
            logger.warning(message)
            return CentralityTable()

    def _get_as_path(self, rel_graph: ASRelGraph, src_as: ASN, dst_as: ASN) -> ASPath:
        logger.info(f"Estimating AS path between {src_as} and {dst_as}")

        return rel_graph.get_as_path(src_as, dst_as)
