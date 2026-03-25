import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lk_world_trade import Sankey

_COUNTRIES = [
    "Sri Lanka",
]

_YEARS = [2022]

if __name__ == "__main__":
    for country in _COUNTRIES:
        for year in _YEARS:
            print(f"Generating combined Sankey for {country} {year} ...")
            Sankey.draw_combined(country=country, year=year, other_threshold=0.01)
            print(f"  Done.")
