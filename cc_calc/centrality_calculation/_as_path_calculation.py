from cc_calc.as_path_estimation import (
    ASPath,
    ASRelGraphError,
    ASRelGraphRepository,
    ASRelGraphRepositoryError,
)
from cc_calc.autonomous_system_number import ASN


class ASPathCalculationError(Exception):
    pass


class ASPathCalculation:
    def __init__(self, as_rel_graph_repo: ASRelGraphRepository) -> None:
        self._as_rel_graph_repo = as_rel_graph_repo

    def estimate_as_path(self, src_as: ASN, dst_as: ASN) -> ASPath:
        try:
            rel_graph = self._as_rel_graph_repo.load_rel_graph()
            as_path = rel_graph.get_as_path(src_as, dst_as)
            return as_path
        except ASRelGraphRepositoryError as e:
            raise ASPathCalculationError(
                "One of the input ASNs is not in the relationship graph"
            ) from e
        except ASRelGraphError as e:
            raise ASPathCalculationError(
                f"Could not calculate path between ASes {src_as} and {dst_as}"
            ) from e
