import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lk_world_trade import Sankey

_IMPORTERS = [
    "Sri Lanka",
]

_YEARS = [2022, 2023]

if __name__ == "__main__":
    for importer in _IMPORTERS:
        for year in _YEARS:
            print(f"Generating import Sankey for {importer} {year} ...")
            Sankey.draw(importer=importer, year=year, other_threshold=0.01)
            print(f"  Done.")
