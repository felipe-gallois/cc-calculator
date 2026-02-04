from abc import ABC, abstractmethod

type AS = str


class ASRelGraphError(Exception):
    pass


class ASRelLoadingError(Exception):
    pass


class ASRelGraph(ABC):
    @abstractmethod
    def bgp_receivers_from_as(self, curr_as: AS, prev_as: AS | None = None) -> set[AS]:
        pass


class ASRelLoader(ABC):
    @abstractmethod
    def load_rel_graph(self) -> ASRelGraph:
        pass
