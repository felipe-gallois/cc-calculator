from collections.abc import Sequence
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.as_path_estimation import ASPath
from cc_calc.autonomous_system import AS, ASRepository, ASRepositoryError
from cc_calc.autonomous_system_number import ASN
from cc_calc.country_code import Alpha2Code, CountryCode
from cc_calc.country_path_estimation._country_path import CountryPath
from cc_calc.country_path_estimation._country_path_estimation import (
    CountryPathEstimation,
    CountryPathEstimationError,
)


def as_repo_mock(
    mocker: MockerFixture, asn_list: Sequence[ASN], country_list: Sequence[CountryCode]
) -> MagicMock:
    as_map = {asn: AS(asn, country) for asn, country in zip(asn_list, country_list)}

    repo_mock = mocker.create_autospec(ASRepository)
    repo_mock.load_as.side_effect = lambda asn: as_map[asn]

    return repo_mock


def test_when_as_path_is_empty_returns_empty_country_path(
    mocker: MockerFixture,
) -> None:
    repo_mock = as_repo_mock(mocker, asn_list=[], country_list=[])
    path_est = CountryPathEstimation(repo_mock)

    country_path = path_est.estimate_country_path(ASPath([]))

    assert country_path == CountryPath([])


def test_when_as_path_has_one_as_returns_path_with_as_country(
    mocker: MockerFixture,
) -> None:
    asns = [ASN(65536)]
    countries = [Alpha2Code("BR")]

    repo_mock = as_repo_mock(mocker, asn_list=asns, country_list=countries)
    path_est = CountryPathEstimation(repo_mock)

    country_path = path_est.estimate_country_path(ASPath(asns))

    assert country_path == CountryPath(countries)


def test_when_as_path_has_two_ases_returns_path_with_as_countries(
    mocker: MockerFixture,
) -> None:
    asns = [ASN(65536), ASN(65537)]
    countries = [Alpha2Code("BR"), Alpha2Code("US")]

    repo_mock = as_repo_mock(mocker, asn_list=asns, country_list=countries)
    path_est = CountryPathEstimation(repo_mock)

    country_path = path_est.estimate_country_path(ASPath(asns))

    assert country_path == CountryPath(countries)


def test_when_as_repo_raises_exception_propagates_it(
    mocker: MockerFixture,
) -> None:
    repo_mock = mocker.create_autospec(ASRepository)
    repo_mock.load_as.side_effect = ASRepositoryError("Repo error")

    path_est = CountryPathEstimation(repo_mock)

    with pytest.raises(CountryPathEstimationError):
        path_est.estimate_country_path(ASPath([ASN(65536)]))
