from abc import ABC, abstractmethod
from typing import Any, Self

_MIN_ASN = 0
_MAX_ASN = 2**32 - 1


class ASNRangeError(Exception):
    def __init__(self, number: int) -> None:
        self.number = number
        super().__init__(f"ASN must be between {_MIN_ASN} and {_MAX_ASN}, got {number}")


class ASNLoadingError(Exception):
    def __init__(self) -> None:
        super().__init__("could not read ASN database")


class ASN:
    def __init__(self, number: int | str) -> None:
        self._number = int(number)

        if not (_MIN_ASN <= self._number <= _MAX_ASN):
            raise ASNRangeError(self._number)

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

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        return self


class ASNRepository(ABC):
    @abstractmethod
    def load_all_asns(self) -> set[ASN]:
        pass
