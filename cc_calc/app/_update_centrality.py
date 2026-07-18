import logging

from cc_calc.core import (
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
            updated_countries: set[CountryCode] = set()

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
                        and not asn_country in updated_countries
                    ):
                        update.add(asn_country, total_weight)
                        updated_countries.add(asn_country)
                except KeyError:
                    self.logger.warning(
                        "Skipping AS centrality update: AS{asn} is not in repository"
                    )
                    continue

        return update

    def _get_asn_country(self, asn: ASN) -> CountryCode | None:
        _as = self._as_repo.load_as(asn)
        return _as.country_of_registry
