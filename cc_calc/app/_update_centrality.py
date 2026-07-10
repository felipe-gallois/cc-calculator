import logging

from cc_calc.core import (
    Alpha2Code,
    ASN,
    ASPath,
    ASWeightGraph,
    CentralityTable,
    CountryCode,
)
from cc_calc.repo import ASRepo


class CentralityUpdate:
    logger = logging.getLogger(__name__)

    def __init__(self, as_repo: ASRepo) -> None:
        self._as_repo = as_repo

    def execute(
        self, path: ASPath, weight_graph: ASWeightGraph, pivot: CountryCode
    ) -> CentralityTable:
        update = CentralityTable()

        src_weight = weight_graph.get_as_weights(path.start)[pivot]

        for dst_country, dst_weight in weight_graph.get_as_weights(path.end).items():
            total_weight = src_weight * dst_weight

            update.add_global(total_weight)
            update.add_excused(pivot, total_weight)
            update.add_excused(dst_country, total_weight)

            for asn in path:
                try:
                    asn_country = self._get_asn_country(asn)

                    if (
                        asn_country is not None
                        and asn_country != pivot
                        and asn_country != dst_country
                    ):
                        is_not_updated = update.get(asn_country) == 0

                        if is_not_updated:
                            update.add(asn_country, total_weight)
                except KeyError:
                    self.logger.warning(
                        "Skipping AS centrality update: AS{asn} is not in repository"
                    )
                    continue

        return update

    def _get_asn_country(self, asn: ASN) -> CountryCode | None:
        _as = self._as_repo.load_as(asn)
        return _as.country_of_registry
