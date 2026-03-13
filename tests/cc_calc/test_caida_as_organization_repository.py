from io import StringIO

from cc_calc.caida_as_organization_repository import _text_to_asn_country_map


def test_when_input_has_single_org_returns_correct_map() -> None:
    input = StringIO(
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
    )

    asn_to_country = _text_to_asn_country_map(input)

    assert asn_to_country == {"65536": "US"}
