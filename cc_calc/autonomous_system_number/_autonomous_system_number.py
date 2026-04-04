from abc import ABC, abstractmethod

_MAX_ASN = 2**32 - 1


class ASNError(Exception):
    pass


class ASNRepositoryError(Exception):
    pass


class ASN:
    def __init__(self, number: int | str) -> None:
        try:
            self._number = int(number)
        except ValueError:
            raise ASNError(f"{number} is not a valid autonomous system number")

        if not (0 <= self._number <= _MAX_ASN):
            raise ASNError(f"{self._number} is not a valid autonomous system number")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ASN):
            return NotImplemented

        return self._number == other._number

    def __repr__(self) -> str:
        return f"ASN({self._number})"

    def __str__(self) -> str:
        return f"{self._number}"

    def __hash__(self) -> int:
        return hash(self._number)


class ASNRepository(ABC):
    @abstractmethod
    def load_all_asns(self) -> set[ASN]:
        pass
