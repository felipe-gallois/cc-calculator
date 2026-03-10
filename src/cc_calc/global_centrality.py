"""Global centrality."""

from typing import Self


class GlobalCentrality:
    """The centrality value of the world."""

    def __init__(self) -> None:
        self._gc = 0

    def __iadd__(self, other: object) -> Self:
        if isinstance(other, int):
            self.add(other)
            return self

        return NotImplemented

    def __int__(self) -> int:
        return self.get()

    def add(self, points: int) -> None:
        """Adds centrality points to the global centrality.

        Args:
            points: The number of points.
        """
        self._gc += points

    def get(self) -> int:
        """Retrieves the centrality value.

        Returns: The centrality value.
        """
        return self._gc
