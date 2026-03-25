import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json
import unittest

from lk_world_trade import TradeInfo
from lk_world_trade._country import get_iso3
from lk_world_trade._product import to_wits_product_group


class TestCountryLookup(unittest.TestCase):
    def test_sri_lanka_iso3(self):
        self.assertEqual(get_iso3("Sri Lanka"), "LKA")

    def test_singapore_iso3(self):
        self.assertEqual(get_iso3("Singapore"), "SGP")

    def test_case_insensitive(self):
        self.assertEqual(get_iso3("sri lanka"), "LKA")

    def test_unknown_country_raises(self):
        with self.assertRaises(ValueError):
            get_iso3("Atlantis")


class TestProductMapping(unittest.TestCase):
    def test_hs6_fuels(self):
        self.assertEqual(to_wits_product_group("271000"), "27-27_Fuels")

    def test_hs6_electronics(self):
        self.assertEqual(to_wits_product_group("854232"), "84-85_MachElec")

    def test_hs6_textiles(self):
        self.assertEqual(to_wits_product_group("620342"), "50-63_TextCloth")

    def test_wits_group_passthrough(self):
        self.assertEqual(to_wits_product_group("Total"), "Total")
        self.assertEqual(to_wits_product_group("27-27_Fuels"), "27-27_Fuels")

    def test_invalid_code_raises(self):
        with self.assertRaises(ValueError):
            to_wits_product_group("INVALID")


class TestReadmeExample(unittest.TestCase):
    """Tests that the exact examples from README.md work and return expected output."""

    def test_readme_example_1_single_country(self):
        trade_info = TradeInfo.get(
            product_code="27-27_Fuels",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2022,
        )
        output = json.loads(str(trade_info))
        self.assertIn("27-27_Fuels", output)
        self.assertIn("Singapore", output["27-27_Fuels"])
        self.assertAlmostEqual(
            output["27-27_Fuels"]["Singapore"], 524778076.47, delta=1.0
        )

    def test_readme_example_2_all_countries(self):
        trade_info = TradeInfo.get(
            product_code="27-27_Fuels",
            importer="Sri Lanka",
            year=2022,
        )
        output = json.loads(str(trade_info))
        self.assertIn("27-27_Fuels", output)
        by_country = output["27-27_Fuels"]
        self.assertIsInstance(by_country, dict)
        self.assertGreater(len(by_country), 0)
        # No regional aggregates (e.g. World, South Asia) in the result
        self.assertNotIn("World", by_country)
        self.assertNotIn("South Asia", by_country)
        # Top exporter for LKA fuels imports in 2022 is India
        top_exporter = max(by_country, key=by_country.__getitem__)
        self.assertEqual(top_exporter, "India")
        self.assertAlmostEqual(by_country["India"], 1186061729.66, delta=1.0)
        self.assertAlmostEqual(
            by_country["Singapore"], 524778076.47, delta=1.0
        )


class TestReadmeExample3(unittest.TestCase):
    """Tests Example 3: all trade (all products, all countries)."""

    def test_readme_example_3_all_trade(self):
        trade_info = TradeInfo.get(
            importer="Sri Lanka",
            year=2022,
        )
        output = json.loads(str(trade_info))
        # Must return multiple product sector group keys, not a single 'Total'
        self.assertGreater(len(output), 1)
        self.assertNotIn("Total", output)
        # Known sector groups that LKA actively trades in
        self.assertIn("27-27_Fuels", output)
        self.assertIn("84-85_MachElec", output)
        self.assertIn("50-63_TextCloth", output)
        # Each product group maps to a non-empty dict of countries
        for group, by_country in output.items():
            self.assertIsInstance(
                by_country, dict, f"{group} value is not a dict"
            )
            self.assertGreater(len(by_country), 0, f"{group} has no countries")
            # No regional aggregates
            self.assertNotIn("World", by_country)
            self.assertNotIn("South Asia", by_country)
        # Spot-check a known value
        self.assertAlmostEqual(
            output["27-27_Fuels"]["India"], 1186061729.66, delta=1.0
        )


class TestReadmeExamples456(unittest.TestCase):
    """Tests Examples 4-6: exporter as the primary country."""

    def test_readme_example_4_exporter_single_product_all_countries(self):
        """Example 4: single product, exporter perspective, all importers."""
        trade_info = TradeInfo.get(
            product_code="27-27_Fuels",
            exporter="Sri Lanka",
            year=2022,
        )
        output = json.loads(str(trade_info))
        self.assertIn("27-27_Fuels", output)
        by_country = output["27-27_Fuels"]
        self.assertIsInstance(by_country, dict)
        self.assertGreater(len(by_country), 0)
        # No regional aggregates
        self.assertNotIn("World", by_country)
        self.assertNotIn("South Asia", by_country)
        # Known top importers of LKA fuel exports in 2022
        self.assertIn("United Arab Emirates", by_country)
        self.assertIn("India", by_country)
        self.assertAlmostEqual(
            by_country["United Arab Emirates"], 71112771.06, delta=1.0
        )
        self.assertAlmostEqual(by_country["India"], 58808726.76, delta=1.0)

    def test_readme_example_5_exporter_all_products_all_countries(self):
        """Example 5: all products, exporter perspective, all importers."""
        trade_info = TradeInfo.get(
            exporter="Sri Lanka",
            year=2022,
        )
        output = json.loads(str(trade_info))
        self.assertGreater(len(output), 1)
        self.assertIn("27-27_Fuels", output)
        for group, by_country in output.items():
            self.assertIsInstance(by_country, dict)
            self.assertGreater(len(by_country), 0)
            self.assertNotIn("World", by_country)

    def test_readme_example_6_both_countries_all_products(self):
        """Example 6: all products, both countries specified — bilateral trade."""
        trade_info = TradeInfo.get(
            importer="India",
            exporter="Sri Lanka",
            year=2022,
        )
        output = json.loads(str(trade_info))
        self.assertGreater(len(output), 1)
        self.assertIn("27-27_Fuels", output)
        # Each group should be keyed by the exporter (Sri Lanka) only
        for group, by_country in output.items():
            self.assertIn("Sri Lanka", by_country)
        self.assertAlmostEqual(
            output["27-27_Fuels"]["Sri Lanka"], 157063719.99, delta=1.0
        )


class TestTradeInfo(unittest.TestCase):
    def test_get_returns_trade_info(self):
        result = TradeInfo.get(
            product_code="27-27_Fuels",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2022,
        )
        self.assertIsInstance(result, TradeInfo)
        self.assertIn("27-27_Fuels", result.data)
        self.assertIn("Singapore", result.data["27-27_Fuels"])
        self.assertGreater(result.data["27-27_Fuels"]["Singapore"], 0)

    def test_str_returns_json(self):
        result = TradeInfo.get(
            product_code="27-27_Fuels",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2022,
        )
        parsed = json.loads(str(result))
        self.assertIn("27-27_Fuels", parsed)
        self.assertIn("Singapore", parsed["27-27_Fuels"])

    def test_product_group_code_directly(self):
        result = TradeInfo.get(
            product_code="Total",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2020,
        )
        self.assertIn("Total", result.data)
        self.assertGreater(result.data["Total"]["Singapore"], 0)


if __name__ == "__main__":
    unittest.main()
