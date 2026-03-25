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
    """Tests that the exact example from README.md works and returns expected output."""

    def test_readme_example(self):
        trade_info = TradeInfo.get(
            product_code="271000",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2022,
        )
        output = json.loads(str(trade_info))
        self.assertEqual(output["product_code"], "271000")
        self.assertEqual(output["importer"], "Sri Lanka")
        self.assertEqual(output["exporter"], "Singapore")
        self.assertEqual(output["year"], 2022)
        self.assertEqual(
            output["product_description"], "Fuels and mineral oils (HS 27)"
        )
        self.assertAlmostEqual(
            output["trade_value_usd"], 524778076.47, delta=1.0
        )


class TestTradeInfo(unittest.TestCase):
    def test_get_returns_trade_info(self):
        result = TradeInfo.get(
            product_code="271000",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2022,
        )
        self.assertIsInstance(result, TradeInfo)
        self.assertEqual(result.product_code, "271000")
        self.assertEqual(result.importer, "Sri Lanka")
        self.assertEqual(result.exporter, "Singapore")
        self.assertEqual(result.year, 2022)
        self.assertIsNotNone(result.trade_value_usd)
        self.assertGreater(result.trade_value_usd, 0)

    def test_str_returns_json(self):
        result = TradeInfo.get(
            product_code="271000",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2022,
        )
        parsed = json.loads(str(result))
        self.assertIn("product_code", parsed)
        self.assertIn("trade_value_usd", parsed)

    def test_product_group_code_directly(self):
        result = TradeInfo.get(
            product_code="Total",
            importer="Sri Lanka",
            exporter="Singapore",
            year=2020,
        )
        self.assertIsNotNone(result.trade_value_usd)
        self.assertGreater(result.trade_value_usd, 0)


if __name__ == "__main__":
    unittest.main()
