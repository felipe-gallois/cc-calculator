"""Country path estimation service."""

from cc_calc.as_country_map import ASCountryMap
from cc_calc.as_path import ASPath
from cc_calc.autonomous_system import AS
from cc_calc.country import Country
from cc_calc.country_path import CountryPath


def _estimate_country(_as: AS, map: ASCountryMap) -> Country | None:
    try:
        return map[_as]
    except KeyError:
        return None


def estimate_path(as_path: ASPath, map: ASCountryMap) -> CountryPath:
    """Estimate the country path of a given AS path.

    Args:
        as_path: The base AS path.
        map: An AS-to-country map.

    Returns: The inferred country path.
    """
    return CountryPath([_estimate_country(_as, map) for _as in as_path])
