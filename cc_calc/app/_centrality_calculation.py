import logging
from itertools import product

from cc_calc.app._update_centrality import (
    CentralityUpdate,
)
from cc_calc.core import (
    ASN,
    ASNRepository,
    ASRelGraph,
    ASRelGraphRepository,
    CentralityTable,
    CountryCode,
    CountrySpecification,
    IPBlockLoadingError,
    IPBlockRepository,
)

logger = logging.getLogger(__name__)


class CentralityCalculation:
    def __init__(
        self,
        ip_block_repo: IPBlockRepository,
        asn_repo: ASNRepository,
        rel_graph_repo: ASRelGraphRepository,
        centrality_update: CentralityUpdate,
    ) -> None:
        self._ip_block_repo = ip_block_repo
        self._asn_repo = asn_repo
        self._rel_graph_repo = rel_graph_repo
        self._centrality_update = centrality_update

    def execute(self, pivot_country: CountryCode) -> CentralityTable:
        centralities = CentralityTable()

        country_asns = self._get_country_asns(pivot_country)
        world_asns = self._asn_repo.load_all_asns()

        rel_graph = self._rel_graph_repo.load_rel_graph()

        for src_as, dst_as in product(country_asns, world_asns):
            centrality_update = self._get_centrality_update(
                rel_graph, pivot_country, src_as, dst_as
            )
            centralities.combine(centrality_update)

        logger.info(
            "Calculated centralities for pivot country",
            extra={"country": pivot_country},
        )

        return centralities

    def _get_country_asns(self, country: CountryCode) -> set[ASN]:
        try:
            country_ip_blocks = self._ip_block_repo.load_blocks_with_specs(
                {CountrySpecification(country)}
            )
            country_asns = {
                block.autonomous_system
                for block in country_ip_blocks
                if block.autonomous_system is not None
            }

            logger.info("Listed country ASes", extra={"country": country})

            return country_asns
        except IPBlockLoadingError:
            message = "Failed calculating centralities: could not list country ASes"
            logger.error(message, extra={"country": country})
            raise

    def _get_centrality_update(
        self,
        rel_graph: ASRelGraph,
        pivot_country: CountryCode,
        src_as: ASN,
        dst_as: ASN,
    ) -> CentralityTable:
        asn_path = rel_graph.get_as_path(src_as, dst_as)
        centrality_update = self._centrality_update.execute(asn_path, pivot_country)
        return centrality_update
