# Sri Lanka's Trade with the World (lk_world_trade)

This Python library is a wrapper for the World Bank's [WITS (World Integrated Trade Solution)](https://wits.worldbank.org/) API, which provides data on a country's international trade with other nations.

- WITS API Documentation: <https://wits.worldbank.org/data/public/WITSAPI_UserGuide.pdf>

## Example Uses

### 1. Trade with a single country for a specific product

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    product_code="271000",
    importer="Sri Lanka",
    exporter="Singapore",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "product_code": "271000",
    "importer": "Sri Lanka",
    "exporter": "Singapore",
    "year": 2022,
    "product_description": "Fuels and mineral oils (HS 27)",
    "trade_value_usd": 524778076.47
}

```

### 2. Trade for a specific product for all countries

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    product_code="271000",
    importer="Sri Lanka",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "product_code": "271000",
    "importer": "Sri Lanka",
    "exporter": null,
    "year": 2022,
    "product_description": "Fuels and mineral oils (HS 27)",
    "trade_value_usd": null,
    "trade_value_usd_by_country": [
        {"exporter": "India", "trade_value_usd": 1186061729.66},
        {"exporter": "Singapore", "trade_value_usd": 524778076.47},
        ...
    ]
}

```

> **Note:** The WITS public API provides trade values at the HS-chapter sector
> level. HS6 codes (e.g. `271000`) are automatically mapped to their WITS product
> sector group (e.g. `27-27_Fuels`). Trade values are in USD.
