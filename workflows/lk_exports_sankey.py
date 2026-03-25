import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lk_world_trade import Sankey

_EXPORTERS = [
    "Sri Lanka",
]

_YEARS = [2022]

if __name__ == "__main__":
    for exporter in _EXPORTERS:
        for year in _YEARS:
            print(f"Generating export Sankey for {exporter} {year} ...")
            Sankey.draw_exports(
                exporter=exporter, year=year, other_threshold=0.01
            )
            print(f"  Done.")
