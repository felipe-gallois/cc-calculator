"""Prefix information and utilities."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from cc_calc.autonomous_system import AS
from cc_calc.country import Country
from cc_calc.ip_prefix._ip_prefix import IPPrefix


@dataclass
class PrefixInfo:
    """IP prefix infomation.

    Attributes:
        prefix: The prefix.
        owner_as: The AS that owns the prefix.
        country: The country in which the prefix resides.
    """

    prefix: IPPrefix
    owner_as: AS | None
    country: Country | None


class PrefixInfoRepository(ABC):
    """Repository of IP prefix information."""

    @abstractmethod
    def load_prefix_info(self, prefix: IPPrefix) -> PrefixInfo:
        """Loads prefix information for an IP prefix.

        Args:
            prefix: The prefix.

        Returns: A prefix information object.
        """
        pass
