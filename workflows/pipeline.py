import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lk_world_trade import TradeInfo

if __name__ == "__main__":
    trade_info = TradeInfo.get(
        product_code="271000",
        importer="Sri Lanka",
        exporter="Singapore",
        year=2022,
    )
    print(trade_info)
