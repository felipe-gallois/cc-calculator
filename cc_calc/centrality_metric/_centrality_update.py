"""Country centrality update service."""

import math

from cc_calc.centrality_metric._centrality_table import CentralityTable
from cc_calc.country_path import CountryPath


def update_centrality(
    path: CountryPath,
    prefix_weights: tuple[int, int],
    centralities: CentralityTable | None = None,
) -> CentralityTable:
    """Updates country centrality by informing a new path.

    Args:
        path: The path that updates the centrality count.
        prefix_weights: The weights of the origin and destination IP prefixes.
        centralities: The previous centrality counts, if they exist.

    Returns: The updated centrality counts.
    """
    if centralities is None:
        centralities = CentralityTable()

    if len(path) >= 3:
        origin = path[0]
        destination = path[-1]

        centrality_gain = math.prod(prefix_weights)

        countries = {
            country
            for country in path
            if (country != origin) and (country != destination)
        }

        for country in countries:
            centralities.add(country, centrality_gain)

    return centralities
