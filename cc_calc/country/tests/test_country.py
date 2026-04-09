from cc_calc.autonomous_system_number import ASN
from cc_calc.country._country import Country
from cc_calc.country_code import Alpha2Code


class TestGetCountryCode:
    def test_when_object_created_can_get_code(self) -> None:
        country = Country(Alpha2Code("BR"))
        assert country.code == Alpha2Code("BR")

        country = Country(Alpha2Code("US"))
        assert country.code == Alpha2Code("US")


class TestListSpannedASes:
    def test_when_no_as_is_added_list_of_spanned_ases_is_empty(self) -> None:
        country = Country(Alpha2Code("BR"))
        assert country.spanned_ases == set()

    def test_when_one_as_is_added_list_of_spanned_ases_has_just_the_as(self) -> None:
        country = Country(Alpha2Code("BR"))
        country.add_as(ASN(65536))
        assert country.spanned_ases == {ASN(65536)}

    def test_when_spanned_as_set_is_modified_country_state_is_not_changed(self) -> None:
        country = Country(Alpha2Code("BR"))
        spanned_ases = country.spanned_ases
        spanned_ases.add(ASN(65536))
        assert country.spanned_ases == set()
