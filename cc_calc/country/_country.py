"""Country object and utilities."""


class CountryError(Exception):
    """Any error raised by a Country."""

    pass


class Country:
    """A country."""

    def __init__(self, code: str):
        """Initializes the Country object.

        Args:
            code: The alpha-2 code that represents the country.

        Raises:
            CountryError: If code is not in alpha-2 format.
        """
        if len(code) != 2 or (not code.isalpha()):
            raise CountryError(f"{code} is an invalid alpha-2 country code")

        self._alpha2 = code.upper()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Country):
            return False

        return self._alpha2 == other._alpha2

    def __hash__(self) -> int:
        return hash(self._alpha2)

    def __repr__(self) -> str:
        return f"Country('{self._alpha2}')"

    def __str__(self) -> str:
        return self._alpha2
