from collections.abc import Iterator, Sequence
from typing import overload

from cc_calc.core._autonomous_system_number import ASN


class ASPath:
    def __init__(self, path: Sequence[int | str | ASN]) -> None:
        self._path = tuple(ASN(x) if not isinstance(x, ASN) else x for x in path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ASPath):
            return NotImplemented

        if len(self._path) != len(other._path):
            return False

        return all([True if x == y else False for x, y in zip(self._path, other._path)])

    def __hash__(self) -> int:
        return hash(self._path)

    def __repr__(self) -> str:
        return f"ASPath({self._path})"

    def __str__(self) -> str:
        path_str = [str(x) for x in self._path]
        return f"{'|'.join(path_str)}"

    def __len__(self) -> int:
        return len(self._path)

    def __iter__(self) -> Iterator[ASN]:
        for _as in self._path:
            yield _as

    @overload
    def __getitem__(self, key: int) -> ASN:
        pass

    @overload
    def __getitem__(self, key: slice) -> "ASPath":
        pass

    def __getitem__(self, key: int | slice) -> ASN | "ASPath":
        if isinstance(key, slice):
            return ASPath(self._path[key])

        return self._path[key]

    @property
    def start(self) -> ASN:
        return self._path[0]

    @property
    def end(self) -> ASN:
        return self._path[-1]

    def peek(self) -> ASN | None:
        if len(self) < 1:
            return None

        return self._path[0]

    def append(self, _as: ASN) -> "ASPath":
        new_sequence = self._path + (_as,)
        return ASPath(new_sequence)
