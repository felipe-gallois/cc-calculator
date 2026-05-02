from cc_calc.as_path_estimation import ASPath
from cc_calc.centrality_calculation._country_path_estimation import (
    CountryPathEstimation,
)
from cc_calc.centrality_calculation._ip_weight_calculation import (
    calculate_ip_weight,
)
from cc_calc.centrality_metric import CentralityTable
from cc_calc.country_code import CountryCode
from cc_calc.ip_block import (
    ASSpecification,
    CountrySpecification,
    IPBlockRepository,
)


class CentralityUpdate:
    def __init__(
        self,
        country_path_estimation: CountryPathEstimation,
        ip_block_repo: IPBlockRepository,
    ) -> None:
        self._country_path_estimation = country_path_estimation
        self._ip_block_repo = ip_block_repo

    def execute(
        self,
        as_path: ASPath,
        src_country: CountryCode,
    ) -> CentralityTable:
        table = CentralityTable()

        src_country_blocks = self._ip_block_repo.load_blocks_with_specs(
            {ASSpecification(as_path[0]), CountrySpecification(src_country)}
        )

        dst_as_blocks = self._ip_block_repo.load_blocks_with_specs(
            {ASSpecification(as_path[-1])}
        )

        country_path = self._country_path_estimation.estimate_country_path(as_path)

        for country in country_path.countries:
            if country == src_country:
                continue

            accounted_dst_blocks = {
                block for block in dst_as_blocks if block.country != country
            }

            weight = calculate_ip_weight(src_country_blocks, accounted_dst_blocks)
            table.add(country, weight)

        return table
