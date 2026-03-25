import json
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from utils import WWW

from ._country import get_group_iso3_set, get_iso3
from ._product import product_group_description, to_wits_product_group

_WITS_SDMX_BASE = (
    "https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade"
    "/reporter/{reporter}/year/{year}/partner/{partner}"
    "/product/{product}/indicator/{indicator}?format=json"
)


def _fetch_trade_value(
    reporter_iso3: str,
    partner_iso3: str,
    product_group: str,
    year: int,
    indicator: str,
) -> Optional[float]:
    """Query WITS SDMX API and return the trade value in USD (or None)."""
    url = _WITS_SDMX_BASE.format(
        reporter=reporter_iso3,
        year=year,
        partner=partner_iso3,
        product=product_group,
        indicator=indicator,
    )
    try:
        content = WWW(url).read()
        data = json.loads(content)
        # SDMX JSON structure: dataSets[0].series["0:0:0:0:0"].observations["0"][0]
        series = data["dataSets"][0]["series"]
        obs_key = next(iter(series))
        observations = series[obs_key]["observations"]
        obs_val_key = next(iter(observations))
        value_thousands_usd = observations[obs_val_key][0]
        if value_thousands_usd is None:
            return None
        return (
            float(value_thousands_usd) * 1000
        )  # WITS values are in USD thousands
    except Exception:
        return None


def _fetch_trade_value_by_country(
    reporter_iso3: str,
    product_group: str,
    year: int,
    indicator: str,
) -> List[Dict[str, object]]:
    """Query WITS SDMX API with partner=ALL and return a list of
    {exporter, trade_value_usd} dicts sorted by trade_value_usd descending."""
    url = _WITS_SDMX_BASE.format(
        reporter=reporter_iso3,
        year=year,
        partner="ALL",
        product=product_group,
        indicator=indicator,
    )
    try:
        content = WWW(url).read()
        data = json.loads(content)
        # SDMX JSON: structure.dimensions.series[2] is the PARTNER dimension
        structure = data["structure"]
        partner_dim = next(
            d
            for d in structure["dimensions"]["series"]
            if d["id"] == "PARTNER"
        )
        partner_values = partner_dim[
            "values"
        ]  # [{"id": "SGP", "name": "Singapore"}, ...]
        series = data["dataSets"][0]["series"]
        group_iso3s = get_group_iso3_set()
        results = []
        for series_key, series_data in series.items():
            # Key format: "0:0:<partner_index>:0:0"
            partner_index = int(series_key.split(":")[2])
            partner_entry = partner_values[partner_index]
            partner_iso3 = partner_entry["id"]
            if partner_iso3 in group_iso3s:
                continue  # skip regional/world aggregates
            partner_name = partner_entry["name"]
            observations = series_data.get("observations", {})
            if not observations:
                continue
            obs_val_key = next(iter(observations))
            raw = observations[obs_val_key][0]
            if raw is None:
                continue
            results.append(
                {
                    "exporter": partner_name,
                    "trade_value_usd": float(raw) * 1000,
                }
            )
        results.sort(key=lambda x: x["trade_value_usd"], reverse=True)
        return results
    except Exception:
        return []


@dataclass
class TradeInfo:
    """Bilateral trade information for a product between two countries.

    Trade values are sourced from the World Bank WITS tradestats-trade dataset
    via the SDMX API (https://wits.worldbank.org).

    Note: The WITS public API provides trade values at the sector/product-group
    level. HS6 product codes are mapped to the corresponding WITS sector group
    (e.g. '271000' → '27-27_Fuels').
    """

    product_code: str
    importer: str
    exporter: Optional[str]
    year: int
    product_description: str
    trade_value_usd: Optional[float]
    trade_value_usd_by_country: Optional[List[Dict[str, object]]] = field(
        default=None
    )

    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def get(
        cls,
        product_code: str,
        importer: str,
        year: int,
        exporter: Optional[str] = None,
    ) -> "TradeInfo":
        """Fetch bilateral trade data from the WITS API.

        Args:
            product_code: An HS6 code (e.g. '271000') or a WITS product group
                code (e.g. 'Total', '27-27_Fuels'). HS6 codes are mapped to
                the appropriate WITS sector group.
            importer: Importing country name (e.g. 'Sri Lanka').
            year: Reference year (e.g. 2022).
            exporter: Exporting country name (e.g. 'Singapore'). When omitted
                or None, returns the world-total import value ('World').

        Returns:
            A TradeInfo instance with the import trade value.

        Raises:
            ValueError: If the country name or product code cannot be resolved.
        """
        importer_iso3 = get_iso3(importer)
        wits_group = to_wits_product_group(product_code)
        description = product_group_description(wits_group)

        if exporter is None:
            # All-countries mode: return per-country breakdown
            by_country = _fetch_trade_value_by_country(
                reporter_iso3=importer_iso3,
                product_group=wits_group,
                year=year,
                indicator="MPRT-TRD-VL",
            )
            return cls(
                product_code=product_code,
                importer=importer,
                exporter=None,
                year=year,
                product_description=description,
                trade_value_usd=None,
                trade_value_usd_by_country=by_country,
            )

        # Single-country mode
        exporter_iso3 = get_iso3(exporter)
        trade_value = _fetch_trade_value(
            reporter_iso3=importer_iso3,
            partner_iso3=exporter_iso3,
            product_group=wits_group,
            year=year,
            indicator="MPRT-TRD-VL",
        )
        return cls(
            product_code=product_code,
            importer=importer,
            exporter=exporter,
            year=year,
            product_description=description,
            trade_value_usd=trade_value,
        )
