# Sri Lanka's Trade with the World (lk_world_trade)

This Python library is a wrapper for the World Bank's [WITS (World Integrated Trade Solution)](https://wits.worldbank.org/) API, which provides data on a country's international trade with other nations.

## Example Use

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    product_code="271000",
    importer="Sri Lanka",
    exporter="Singapore",
    year=2023,
)

print(trade_info)

```

```JSON

{
    "product_code": "271000",
    "importer": "Sri Lanka",
    "exporter": "Singapore",
    "year": 2023,
    "product_description": "Petroleum oils, etc, (excl. crude); preparation",
    "trade_value_usd": 2349473690,
    "quantity": 3207960000,
    "quantity_unit": "Kg"
}

```
