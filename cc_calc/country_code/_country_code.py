from abc import ABC, abstractmethod


class CountryCodeError(Exception):
    pass


class CountryCode(ABC):
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Alpha2Code(CountryCode):
    def __init__(self, code: str):
        if len(code) != 2 or (not code.isalpha()):
            raise CountryCodeError(f"{code} is an invalid alpha-2 country code")

        self._code = code.upper()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alpha2Code):
            return False

        return self._code == other._code

    def __hash__(self) -> int:
        return hash(self._code)

    def __repr__(self) -> str:
        return f"Alpha2Code('{self._code}')"

    def __str__(self) -> str:
        return self._code
