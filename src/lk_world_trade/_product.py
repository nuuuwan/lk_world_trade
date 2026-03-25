# Maps the first two digits of an HS6 code to a WITS product sector group code.
# Sector group codes from WITS_API_ProductGroups.xlsx (tradestats-trade datasource).
_HS2_TO_WITS_SECTOR = {
    "01": "01-05_Animal",
    "02": "01-05_Animal",
    "03": "01-05_Animal",
    "04": "01-05_Animal",
    "05": "01-05_Animal",
    "06": "06-15_Vegetable",
    "07": "06-15_Vegetable",
    "08": "06-15_Vegetable",
    "09": "06-15_Vegetable",
    "10": "06-15_Vegetable",
    "11": "06-15_Vegetable",
    "12": "06-15_Vegetable",
    "13": "06-15_Vegetable",
    "14": "06-15_Vegetable",
    "15": "06-15_Vegetable",
    "16": "16-24_FoodProd",
    "17": "16-24_FoodProd",
    "18": "16-24_FoodProd",
    "19": "16-24_FoodProd",
    "20": "16-24_FoodProd",
    "21": "16-24_FoodProd",
    "22": "16-24_FoodProd",
    "23": "16-24_FoodProd",
    "24": "16-24_FoodProd",
    "25": "25-26_Minerals",
    "26": "25-26_Minerals",
    "27": "27-27_Fuels",
    "28": "28-38_Chemicals",
    "29": "28-38_Chemicals",
    "30": "28-38_Chemicals",
    "31": "28-38_Chemicals",
    "32": "28-38_Chemicals",
    "33": "28-38_Chemicals",
    "34": "28-38_Chemicals",
    "35": "28-38_Chemicals",
    "36": "28-38_Chemicals",
    "37": "28-38_Chemicals",
    "38": "28-38_Chemicals",
    "39": "39-40_PlastiRub",
    "40": "39-40_PlastiRub",
    "41": "41-43_HidesSkin",
    "42": "41-43_HidesSkin",
    "43": "41-43_HidesSkin",
    "44": "44-49_Wood",
    "45": "44-49_Wood",
    "46": "44-49_Wood",
    "47": "44-49_Wood",
    "48": "44-49_Wood",
    "49": "44-49_Wood",
    "50": "50-63_TextCloth",
    "51": "50-63_TextCloth",
    "52": "50-63_TextCloth",
    "53": "50-63_TextCloth",
    "54": "50-63_TextCloth",
    "55": "50-63_TextCloth",
    "56": "50-63_TextCloth",
    "57": "50-63_TextCloth",
    "58": "50-63_TextCloth",
    "59": "50-63_TextCloth",
    "60": "50-63_TextCloth",
    "61": "50-63_TextCloth",
    "62": "50-63_TextCloth",
    "63": "50-63_TextCloth",
    "64": "64-67_Footwear",
    "65": "64-67_Footwear",
    "66": "64-67_Footwear",
    "67": "64-67_Footwear",
    "68": "68-71_StoneGlas",
    "69": "68-71_StoneGlas",
    "70": "68-71_StoneGlas",
    "71": "68-71_StoneGlas",
    "72": "72-83_Metals",
    "73": "72-83_Metals",
    "74": "72-83_Metals",
    "75": "72-83_Metals",
    "76": "72-83_Metals",
    "77": "72-83_Metals",
    "78": "72-83_Metals",
    "79": "72-83_Metals",
    "80": "72-83_Metals",
    "81": "72-83_Metals",
    "82": "72-83_Metals",
    "83": "72-83_Metals",
    "84": "84-85_MachElec",
    "85": "84-85_MachElec",
    "86": "86-89_Transport",
    "87": "86-89_Transport",
    "88": "86-89_Transport",
    "89": "86-89_Transport",
    "90": "90-99_Miscellan",
    "91": "90-99_Miscellan",
    "92": "90-99_Miscellan",
    "93": "90-99_Miscellan",
    "94": "90-99_Miscellan",
    "95": "90-99_Miscellan",
    "96": "90-99_Miscellan",
    "97": "90-99_Miscellan",
    "98": "90-99_Miscellan",
    "99": "90-99_Miscellan",
}

# Known WITS sector group codes (used to detect if a code is already a group code)
_WITS_SECTOR_GROUPS = set(_HS2_TO_WITS_SECTOR.values()) | {
    "Total",
    "AgrRaw",
    "Chemical",
    "Food",
    "Fuels",
    "manuf",
    "OresMtls",
    "Textiles",
    "Transp",
    "UNCTAD-SoP1",
    "UNCTAD-SoP2",
    "UNCTAD-SoP3",
    "UNCTAD-SoP4",
}


def to_wits_product_group(product_code: str) -> str:
    """Convert an HS6 code (e.g. '271000') to its WITS sector group (e.g. '27-27_Fuels').

    If the code is already a known WITS product group, it is returned as-is.
    Raises ValueError for unrecognised codes.
    """
    code = product_code.strip()
    if code in _WITS_SECTOR_GROUPS:
        return code
    # HS codes are numeric; try first-two-digit lookup
    if code.isdigit() and len(code) >= 2:
        prefix = code[:2]
        if prefix in _HS2_TO_WITS_SECTOR:
            return _HS2_TO_WITS_SECTOR[prefix]
    raise ValueError(
        f"Unknown product code '{product_code}'. "
        "Provide a 4-6 digit HS code or a WITS product group code "
        "(e.g. 'Total', '27-27_Fuels')."
    )


def product_group_description(wits_group: str) -> str:
    """Return a human-readable description for a WITS product sector group."""
    _DESCRIPTIONS = {
        "Total": "All products",
        "01-05_Animal": "Animal products (HS 01-05)",
        "06-15_Vegetable": "Vegetable products (HS 06-15)",
        "16-24_FoodProd": "Food products (HS 16-24)",
        "25-26_Minerals": "Minerals (HS 25-26)",
        "27-27_Fuels": "Fuels and mineral oils (HS 27)",
        "28-38_Chemicals": "Chemical products (HS 28-38)",
        "39-40_PlastiRub": "Plastics and rubber (HS 39-40)",
        "41-43_HidesSkin": "Hides, skins and leather (HS 41-43)",
        "44-49_Wood": "Wood and paper products (HS 44-49)",
        "50-63_TextCloth": "Textiles and clothing (HS 50-63)",
        "64-67_Footwear": "Footwear and headgear (HS 64-67)",
        "68-71_StoneGlas": "Stone, glass and precious metals (HS 68-71)",
        "72-83_Metals": "Metals (HS 72-83)",
        "84-85_MachElec": "Machinery and electronics (HS 84-85)",
        "86-89_Transport": "Transport equipment (HS 86-89)",
        "90-99_Miscellan": "Miscellaneous (HS 90-99)",
        "AgrRaw": "Agricultural raw materials",
        "Chemical": "Chemicals",
        "Food": "Food",
        "Fuels": "Fuels",
        "manuf": "Manufactured goods",
        "OresMtls": "Ores and metals",
        "Textiles": "Textiles",
        "Transp": "Transport equipment",
        "UNCTAD-SoP1": "Raw materials",
        "UNCTAD-SoP2": "Intermediate goods",
        "UNCTAD-SoP3": "Consumer goods",
        "UNCTAD-SoP4": "Capital goods",
    }
    return _DESCRIPTIONS.get(wits_group, wits_group)
