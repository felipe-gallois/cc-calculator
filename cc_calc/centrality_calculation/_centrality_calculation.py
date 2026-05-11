from itertools import product

from cc_calc.as_path_estimation import (
    ASRelGraph,
    ASRelGraphRepository,
)
from cc_calc.autonomous_system_number import ASN, ASNRepository
from cc_calc.centrality_calculation._update_centrality import (
    CentralityUpdate,
)
from cc_calc.centrality_metric import CentralityTable
from cc_calc.country_code import CountryCode
from cc_calc.ip_block import (
    CountrySpecification,
    IPBlockRepository,
)


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

        return centralities

    def _get_country_asns(self, country: CountryCode) -> set[ASN]:
        country_ip_blocks = self._ip_block_repo.load_blocks_with_specs(
            {CountrySpecification(country)}
        )
        return {
            block.autonomous_system
            for block in country_ip_blocks
            if block.autonomous_system is not None
        }

    def _get_centrality_update(
        self,
        rel_graph: ASRelGraph,
        pivot_country: CountryCode,
        src_as: ASN,
        dst_as: ASN,
    ) -> CentralityTable:
        try:
            asn_path = rel_graph.get_as_path(src_as, dst_as)
            return self._centrality_update.execute(asn_path, pivot_country)
        except Exception:
            return CentralityTable()
