from cc_calc.core import CountryCode, CountryPath


def list_in_between_countries(
    country_path: CountryPath, src_country: CountryCode, dst_country: CountryCode
) -> set[CountryCode]:
    return {
        country
        for country in country_path
        if (country != src_country) and (country != dst_country)
    }
