from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.autonomous_system_number import ASN
from cc_calc.country._asn_resolver import ASNResolver, ASNResolverError
from cc_calc.country._country import CountryRepositoryError
from cc_calc.country._country_code import Alpha2Code
from cc_calc.country._file_country_repository import FileCountryRepository


@pytest.fixture
def mock_asn_resolver(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(ASNResolver)


def test_when_asn_resolver_raises_exception_propagates_exception(
    mock_asn_resolver: MagicMock,
) -> None:
    mock_asn_resolver.load_country_asns.side_effect = ASNResolverError(
        "ASN resolver error"
    )

    repository = FileCountryRepository(mock_asn_resolver)

    with pytest.raises(CountryRepositoryError):
        repository.load_country_with_code(Alpha2Code("BR"))


def test_when_asn_resolver_returns_asns_returns_country_with_asns(
    mock_asn_resolver: MagicMock,
) -> None:
    mock_asn_resolver.load_country_asns.side_effect = lambda country: (
        {65536} if country == "BR" else {}
    )

    repository = FileCountryRepository(mock_asn_resolver)

    retrieved_country = repository.load_country_with_code(Alpha2Code("BR"))

    assert retrieved_country.code == Alpha2Code("BR")
    assert retrieved_country.spanned_ases == {ASN(65536)}


def test_when_asn_resolver_returns_two_asns_returns_country_with_both_asns(
    mock_asn_resolver: MagicMock,
) -> None:
    mock_asn_resolver.load_country_asns.side_effect = lambda country: (
        {65536, 65537} if country == "US" else {}
    )

    repository = FileCountryRepository(mock_asn_resolver)

    retrieved_country = repository.load_country_with_code(Alpha2Code("US"))

    assert retrieved_country.code == Alpha2Code("US")
    assert retrieved_country.spanned_ases == {ASN(65536), ASN(65537)}
