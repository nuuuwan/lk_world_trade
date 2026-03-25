import functools
import xml.etree.ElementTree as ET

from utils import WWW

_WITS_COUNTRY_URL = "https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/country/ALL"


@functools.lru_cache(maxsize=1)
def _get_country_map():
    """Return dict mapping lowercase country name → ISO3 code."""
    content = WWW(_WITS_COUNTRY_URL).read()
    root = ET.fromstring(content)
    ns = {"wits": "http://wits.worldbank.org"}
    country_map = {}
    for country in root.findall(".//wits:country", ns):
        iso3 = country.findtext("wits:iso3Code", default="", namespaces=ns)
        name = country.findtext("wits:name", default="", namespaces=ns)
        if iso3 and name:
            country_map[name.lower()] = iso3
    return country_map


def get_iso3(country_name: str) -> str:
    """Look up ISO3 code for a country name.

    Raises ValueError if not found.
    """
    country_map = _get_country_map()
    key = country_name.strip().lower()
    if key in country_map:
        return country_map[key]
    # Partial match fallback
    matches = [iso3 for name, iso3 in country_map.items() if key in name]
    if len(matches) == 1:
        return matches[0]
    raise ValueError(
        f"Country '{country_name}' not found in WITS. "
        f"Use the exact name from https://wits.worldbank.org"
    )
