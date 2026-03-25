# Sri Lanka's Trade with the World (lk_world_trade)

This Python library is a wrapper for the World Bank's [WITS (World Integrated Trade Solution)](https://wits.worldbank.org/) API, which provides data on a country's international trade with other nations.

- WITS API Documentation: <https://wits.worldbank.org/data/public/WITSAPI_UserGuide.pdf>

## Example Uses

### 1. Trade with a single country for a specific product

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    product_code="27-27_Fuels",
    importer="Sri Lanka",
    exporter="Singapore",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "27-27_Fuels": {
        "Singapore": 524778076.47
    }
}

```

### 2. Trade for a specific product for all countries

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    product_code="27-27_Fuels",
    importer="Sri Lanka",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "27-27_Fuels": {
        "India": 1186061729.66,
        "Singapore": 524778076.47,
        ...
    }
}

```

### 3. All trade

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    importer="Sri Lanka",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "01-05_Animal": {
        "India": 45678901.23,
        ...
    },
    "27-27_Fuels": {
        "India": 1186061729.66,
        "Singapore": 524778076.47,
        ...
    },
    ...
}

```

### 4. Exports of a specific product to all countries

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    product_code="27-27_Fuels",
    exporter="Sri Lanka",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "27-27_Fuels": {
        "United Arab Emirates": 71112771.06,
        "India": 58808726.76,
        ...
    }
}

```

### 5. All exports across all products and all countries

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    exporter="Sri Lanka",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "01-05_Animal": {
        "India": 12345678.0,
        ...
    },
    "27-27_Fuels": {
        "United Arab Emirates": 71112771.06,
        ...
    },
    ...
}

```

### 6. All trade between two specific countries across all products

```python
from lk_world_trade import TradeInfo

trade_info = TradeInfo.get(
    importer="India",
    exporter="Sri Lanka",
    year=2022,
)

print(trade_info)

```

```JSON

{
    "01-05_Animal": {
        "Sri Lanka": 12345678.0
    },
    "27-27_Fuels": {
        "Sri Lanka": 157063719.99
    },
    ...
}

```

> **Note:** The WITS public API provides trade values at the HS-chapter sector
> level. HS6 codes (e.g. `271000`) are automatically mapped to their WITS product
> sector group (e.g. `27-27_Fuels`). Trade values are in USD.

## Visualisation

### 7. Sankey diagram of all imports

```python
from lk_world_trade import Sankey

Sankey.draw(
    importer="Sri Lanka",
    year=2022,
    other_threshold=0.02,  # flows < 2% of total grouped as "Other"
)

```

Generates an interactive Sankey diagram showing trade flows:

```
Product Group  ──►  Exporter Country  ──►  Sri Lanka
```

Each node width and link thickness is proportional to trade value (USD). The
diagram opens in a browser window via Plotly and is saved as
`images/sankey_Sri_Lanka_2022.png` in the project root.
