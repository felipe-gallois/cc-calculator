from cc_calc.core import ASN, Alpha2Code, ASWeightGraph, IPBlock, IPPrefix
from cc_calc.repo._database import IPPrefixDB, PrefixASNDB, PrefixCountryDB


class ASWeightGraphRepo:
    def __init__(
        self,
        prefix_source: IPPrefixDB,
        asn_res: PrefixASNDB,
        country_res: PrefixCountryDB,
    ) -> None:
        self._prefix_source = prefix_source
        self._asn_res = asn_res
        self._country_res = country_res

    def load_weight_graph(self) -> ASWeightGraph:
        graph = ASWeightGraph()

        for ip_prefix_dto in self._prefix_source.load_all_ip_prefixes():
            asn_dto = self._asn_res.load_prefix_asn(ip_prefix_dto)
            country_dto = self._country_res.load_prefix_country(ip_prefix_dto)

            if (asn_dto is not None) and (country_dto is not None):
                ip_prefix = IPPrefix(ip_prefix_dto)
                asn = ASN(asn_dto)
                country = Alpha2Code(country_dto)
                graph.add_ip_block(IPBlock(ip_prefix, country, asn))

        return graph
