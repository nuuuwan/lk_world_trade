import json
from dataclasses import asdict, dataclass
from typing import Optional

from utils import WWW

from ._country import get_iso3
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
    exporter: str
    year: int
    product_description: str
    trade_value_usd: Optional[float]

    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def get(
        cls,
        product_code: str,
        importer: str,
        exporter: str,
        year: int,
    ) -> "TradeInfo":
        """Fetch bilateral trade data from the WITS API.

        Args:
            product_code: An HS6 code (e.g. '271000') or a WITS product group
                code (e.g. 'Total', '27-27_Fuels'). HS6 codes are mapped to
                the appropriate WITS sector group.
            importer: Importing country name (e.g. 'Sri Lanka').
            exporter: Exporting country name (e.g. 'Singapore').
            year: Reference year (e.g. 2022).

        Returns:
            A TradeInfo instance with the bilateral import trade value.

        Raises:
            ValueError: If the country name or product code cannot be resolved.
        """
        importer_iso3 = get_iso3(importer)
        exporter_iso3 = get_iso3(exporter)
        wits_group = to_wits_product_group(product_code)
        description = product_group_description(wits_group)

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
