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


@functools.lru_cache(maxsize=1)
def get_group_iso3_set() -> frozenset:
    """Return the set of ISO3 codes that are regional/group aggregates in WITS."""
    content = WWW(_WITS_COUNTRY_URL).read()
    root = ET.fromstring(content)
    ns = {"wits": "http://wits.worldbank.org"}
    groups = set()
    for country in root.findall(".//wits:country", ns):
        if country.get("isgroup", "No") == "Yes":
            iso3 = country.findtext("wits:iso3Code", default="", namespaces=ns)
            if iso3:
                groups.add(iso3)
    return frozenset(groups)


@functools.lru_cache(maxsize=1)
def get_group_name_set() -> frozenset:
    """Return the set of country names that are regional/group aggregates in WITS."""
    content = WWW(_WITS_COUNTRY_URL).read()
    root = ET.fromstring(content)
    ns = {"wits": "http://wits.worldbank.org"}
    groups = set()
    for country in root.findall(".//wits:country", ns):
        if country.get("isgroup", "No") == "Yes":
            name = country.findtext("wits:name", default="", namespaces=ns)
            if name:
                groups.add(name)
    return frozenset(groups)


_WORLD_NAMES = {"world", "all", "wld"}
_WORLD_ISO3 = "WLD"


def get_iso3(country_name: str) -> str:
    """Look up ISO3 code for a country name.

    Pass 'World' (or 'All' / 'WLD') to get the world-total partner code.
    Raises ValueError if not found.
    """
    key = country_name.strip().lower()
    if key in _WORLD_NAMES:
        return _WORLD_ISO3
    country_map = _get_country_map()
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
