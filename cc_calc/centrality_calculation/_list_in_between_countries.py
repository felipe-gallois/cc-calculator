from cc_calc.country_code import CountryCode
from cc_calc.country_path import CountryPath


def list_in_between_countries(
    country_path: CountryPath, src_country: CountryCode, dst_country: CountryCode
) -> set[CountryCode]:
    return {
        country
        for country in country_path
        if (country != src_country) and (country != dst_country)
    }
