import os

import plotly.graph_objects as go

from ._trade_info import TradeInfo

_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "images")

# Semantic colors keyed by WITS sector group code
_PRODUCT_COLORS: dict[str, str] = {
    "01-05_Animal": "#C8A05A",  # tan/leather – animal products
    "06-15_Vegetable": "#4CAF50",  # green – vegetable/plant
    "16-24_FoodProd": "#FF9800",  # amber – processed food
    "25-26_Minerals": "#9E9E9E",  # stone grey – minerals/rock
    "27-27_Fuels": "#212121",  # near-black – coal/oil
    "28-38_Chemicals": "#7986CB",  # indigo – chemicals/lab
    "39-40_PlastiRub": "#00BCD4",  # cyan – plastic/synthetic
    "41-43_HidesSkin": "#8D6E63",  # brown – hides/leather
    "44-49_Wood": "#795548",  # wood brown
    "50-63_TextCloth": "#E91E63",  # pink/rose – textiles
    "64-67_Footwear": "#FF5722",  # deep orange – footwear
    "68-71_StoneGlas": "#B0BEC5",  # light grey-blue – glass/stone
    "72-83_Metals": "#607D8B",  # steel blue-grey – metals
    "84-85_MachElec": "#1565C0",  # deep blue – machinery/electronics
    "86-89_Transport": "#F44336",  # red – transport
    "90-99_Miscellan": "#AB47BC",  # purple – miscellaneous
}
_FALLBACK_COLOR = "#636EFA"

# Human-readable short names for WITS sector groups
_PRODUCT_LABELS: dict[str, str] = {
    "01-05_Animal": "Animal Products",
    "06-15_Vegetable": "Vegetables",
    "16-24_FoodProd": "Food Products",
    "25-26_Minerals": "Minerals",
    "27-27_Fuels": "Fuels",
    "28-38_Chemicals": "Chemicals",
    "39-40_PlastiRub": "Plastics & Rubber",
    "41-43_HidesSkin": "Hides & Skins",
    "44-49_Wood": "Wood & Paper",
    "50-63_TextCloth": "Textiles & Clothing",
    "64-67_Footwear": "Footwear",
    "68-71_StoneGlas": "Stone & Glass",
    "72-83_Metals": "Metals",
    "84-85_MachElec": "Machinery & Electronics",
    "86-89_Transport": "Transport Equipment",
    "90-99_Miscellan": "Miscellaneous",
}

_OTHER_LABEL = "Other"
_OTHER_COLOR = "#AAAAAA"


def _product_color(code: str) -> str:
    return _PRODUCT_COLORS.get(code, _FALLBACK_COLOR)


def _product_label(code: str) -> str:
    return _PRODUCT_LABELS.get(code, code)


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a 6-digit hex colour + alpha to an rgba() string."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _fmt_musd(val: float) -> str:
    """Format a USD value as a compact Million/Billion string."""
    m = val / 1_000_000
    if m >= 1000:
        return f"${m / 1000:.1f}B"
    return f"${m:.0f}M"


class Sankey:
    """Sankey diagram visualisation of trade flows.

    Both import and export diagrams share the same three-column layout:

        left  →  middle (product groups)  →  right

    For imports:  exporter countries  →  products  →  importer (single node)
    For exports:  exporter (single node)  →  products  →  importer countries

    Nodes below ``other_threshold`` × grand total are collapsed into "Other".
    """

    @staticmethod
    def _render(
        raw: dict,
        focal_label: str,
        country_is_left: bool,
        grand_total: float,
        other_threshold: float,
        title_text: str,
        png_path: str,
    ) -> go.Figure:
        """Shared rendering logic for import and export Sankeys."""
        threshold_value = other_threshold * grand_total

        # Per-dimension totals
        country_totals: dict[str, float] = {}
        for (_, country), value in raw.items():
            country_totals[country] = country_totals.get(country, 0.0) + value

        product_totals: dict[str, float] = {}
        for (product, _), value in raw.items():
            product_totals[product] = product_totals.get(product, 0.0) + value

        # Threshold filtering
        sig_countries = {
            c for c, v in country_totals.items() if v >= threshold_value
        }
        has_other_country = len(sig_countries) < len(country_totals)
        sig_products = sorted(
            p for p, v in product_totals.items() if v >= threshold_value
        )
        has_other_product = len(sig_products) < len(product_totals)

        countries_sorted = sorted(sig_countries)
        product_colors = {p: _product_color(p) for p in sig_products}

        other_country_total = sum(
            v for (_, c), v in raw.items() if c not in sig_countries
        )
        other_product_total = sum(
            v for (p, _), v in raw.items() if p not in set(sig_products)
        )

        # ------------------------------------------------------------------ #
        # Node layout                                                          #
        #                                                                      #
        # imports (country_is_left=True):                                      #
        #   [countries | Other_C | products | Other_P | focal]                #
        #                                                                      #
        # exports (country_is_left=False):                                     #
        #   [focal | products | Other_P | countries | Other_C]                #
        # ------------------------------------------------------------------ #
        if country_is_left:
            c_idx = {c: i for i, c in enumerate(countries_sorted)}
            other_country_idx = (
                len(countries_sorted) if has_other_country else None
            )
            p_base = len(countries_sorted) + (1 if has_other_country else 0)
            p_idx = {p: p_base + i for i, p in enumerate(sig_products)}
            other_product_idx = (
                p_base + len(sig_products) if has_other_product else None
            )
            focal_idx = (
                p_base + len(sig_products) + (1 if has_other_product else 0)
            )

            node_labels = (
                countries_sorted
                + ([_OTHER_LABEL] if has_other_country else [])
                + [_product_label(p) for p in sig_products]
                + (["Other Products"] if has_other_product else [])
                + [focal_label]
            )
            node_totals = (
                [country_totals[c] for c in countries_sorted]
                + ([other_country_total] if has_other_country else [])
                + [product_totals[p] for p in sig_products]
                + ([other_product_total] if has_other_product else [])
                + [grand_total]
            )
            node_colors = (
                ["#888888"] * len(countries_sorted)
                + ([_OTHER_COLOR] if has_other_country else [])
                + [product_colors[p] for p in sig_products]
                + ([_OTHER_COLOR] if has_other_product else [])
                + ["#444444"]
            )
        else:
            focal_idx = 0
            p_idx = {p: 1 + i for i, p in enumerate(sig_products)}
            other_product_idx = (
                1 + len(sig_products) if has_other_product else None
            )
            c_base = 1 + len(sig_products) + (1 if has_other_product else 0)
            c_idx = {c: c_base + i for i, c in enumerate(countries_sorted)}
            other_country_idx = (
                c_base + len(countries_sorted) if has_other_country else None
            )

            node_labels = (
                [focal_label]
                + [_product_label(p) for p in sig_products]
                + (["Other Products"] if has_other_product else [])
                + countries_sorted
                + ([_OTHER_LABEL] if has_other_country else [])
            )
            node_totals = (
                [grand_total]
                + [product_totals[p] for p in sig_products]
                + ([other_product_total] if has_other_product else [])
                + [country_totals[c] for c in countries_sorted]
                + ([other_country_total] if has_other_country else [])
            )
            node_colors = (
                ["#444444"]
                + [product_colors[p] for p in sig_products]
                + ([_OTHER_COLOR] if has_other_product else [])
                + ["#888888"] * len(countries_sorted)
                + ([_OTHER_COLOR] if has_other_country else [])
            )

        node_labels_ann = [
            f"{lbl} ({_fmt_musd(t)})"
            for lbl, t in zip(node_labels, node_totals)
        ]

        # ------------------------------------------------------------------ #
        # Build links                                                          #
        # imports: country → product → focal                                  #
        # exports: focal → product → country                                  #
        # ------------------------------------------------------------------ #
        link_acc: dict[tuple[int, int, str], float] = {}

        for (product, country), value in raw.items():
            country_node = c_idx.get(country, other_country_idx)
            if product in p_idx:
                product_node = p_idx[product]
                link_product = product
            else:
                product_node = other_product_idx
                link_product = _OTHER_LABEL

            if country_is_left:
                k1 = (country_node, product_node, link_product)
                k2 = (product_node, focal_idx, link_product)
            else:
                k1 = (focal_idx, product_node, link_product)
                k2 = (product_node, country_node, link_product)

            link_acc[k1] = link_acc.get(k1, 0.0) + value
            link_acc[k2] = link_acc.get(k2, 0.0) + value

        sources, targets, values, link_colors = [], [], [], []
        for (src, tgt, lp), value in link_acc.items():
            sources.append(src)
            targets.append(tgt)
            values.append(value)
            link_colors.append(
                _rgba(product_colors.get(lp, _OTHER_COLOR), 0.45)
            )

        # Assemble figure
        fig = go.Figure(
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=15,
                    thickness=20,
                    label=node_labels_ann,
                    color=node_colors,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=link_colors,
                ),
            )
        )
        fig.update_layout(title_text=title_text, font_size=11)

        images_dir = os.path.normpath(_IMAGES_DIR)
        os.makedirs(images_dir, exist_ok=True)
        fig.write_image(png_path, width=1600, height=900, scale=2)
        os.system(f"open {png_path}")
        return fig

    @staticmethod
    def draw(
        importer: str, year: int, other_threshold: float = 0.02
    ) -> go.Figure:
        """Sankey of all imports into ``importer`` for ``year``.

        Layout: Exporter countries → Product groups → Importer
        """
        trade_info = TradeInfo.get(importer=importer, year=year)

        raw: dict[tuple[str, str], float] = {}
        for product, by_country in trade_info.data.items():
            for country, value in by_country.items():
                if value and value > 0:
                    raw[(product, country)] = (
                        raw.get((product, country), 0.0) + value
                    )

        grand_total = sum(raw.values())
        if grand_total == 0:
            raise ValueError(f"No trade data found for {importer} in {year}.")

        pct = int(other_threshold * 100)
        title = (
            f"Import Flows into {importer} ({year})<br>"
            f"<sup>Exporter → Product group → Importer (USD)"
            f" · flows &lt;{pct}% of total grouped as 'Other'</sup>"
        )
        safe = importer.replace(" ", "_")
        png_path = os.path.join(
            os.path.normpath(_IMAGES_DIR), f"sankey_imports_{safe}_{year}.png"
        )

        return Sankey._render(
            raw=raw,
            focal_label=importer,
            country_is_left=True,
            grand_total=grand_total,
            other_threshold=other_threshold,
            title_text=title,
            png_path=png_path,
        )

    @staticmethod
    def draw_exports(
        exporter: str, year: int, other_threshold: float = 0.02
    ) -> go.Figure:
        """Sankey of all exports from ``exporter`` for ``year``.

        Layout: Exporter → Product groups → Importer countries
        """
        trade_info = TradeInfo.get(exporter=exporter, year=year)

        raw: dict[tuple[str, str], float] = {}
        for product, by_country in trade_info.data.items():
            for country, value in by_country.items():
                if value and value > 0:
                    raw[(product, country)] = (
                        raw.get((product, country), 0.0) + value
                    )

        grand_total = sum(raw.values())
        if grand_total == 0:
            raise ValueError(f"No trade data found for {exporter} in {year}.")

        pct = int(other_threshold * 100)
        title = (
            f"Export Flows from {exporter} ({year})<br>"
            f"<sup>Exporter → Product group → Importer (USD)"
            f" · flows &lt;{pct}% of total grouped as 'Other'</sup>"
        )
        safe = exporter.replace(" ", "_")
        png_path = os.path.join(
            os.path.normpath(_IMAGES_DIR), f"sankey_exports_{safe}_{year}.png"
        )

        return Sankey._render(
            raw=raw,
            focal_label=exporter,
            country_is_left=False,
            grand_total=grand_total,
            other_threshold=other_threshold,
            title_text=title,
            png_path=png_path,
        )

    @staticmethod
    def draw_combined(
        country: str, year: int, other_threshold: float = 0.02
    ) -> go.Figure:
        """Combined Sankey showing both imports and exports through ``country``.

        Layout (5 columns):
            Import source countries → Import products → Country → Export products → Export destination countries

        The trade balance (surplus or deficit) is shown in the title and the
        focal node label.
        """
        import_info = TradeInfo.get(importer=country, year=year)
        export_info = TradeInfo.get(exporter=country, year=year)

        raw_imports: dict[tuple[str, str], float] = {}
        for product, by_country in import_info.data.items():
            for c, value in by_country.items():
                if value and value > 0:
                    raw_imports[(product, c)] = (
                        raw_imports.get((product, c), 0.0) + value
                    )

        raw_exports: dict[tuple[str, str], float] = {}
        for product, by_country in export_info.data.items():
            for c, value in by_country.items():
                if value and value > 0:
                    raw_exports[(product, c)] = (
                        raw_exports.get((product, c), 0.0) + value
                    )

        total_imports = sum(raw_imports.values())
        total_exports = sum(raw_exports.values())
        if total_imports == 0 and total_exports == 0:
            raise ValueError(f"No trade data found for {country} in {year}.")

        balance = total_exports - total_imports  # positive = surplus

        imp_threshold = other_threshold * total_imports
        exp_threshold = other_threshold * total_exports

        # ── Import-side aggregation ──────────────────────────────────────── #
        imp_ctry_totals: dict[str, float] = {}
        for (_, c), v in raw_imports.items():
            imp_ctry_totals[c] = imp_ctry_totals.get(c, 0.0) + v

        imp_prod_totals: dict[str, float] = {}
        for (p, _), v in raw_imports.items():
            imp_prod_totals[p] = imp_prod_totals.get(p, 0.0) + v

        sig_ic = {c for c, v in imp_ctry_totals.items() if v >= imp_threshold}
        has_other_ic = len(sig_ic) < len(imp_ctry_totals)
        sig_ip = sorted(
            p for p, v in imp_prod_totals.items() if v >= imp_threshold
        )
        has_other_ip = len(sig_ip) < len(imp_prod_totals)

        # ── Export-side aggregation ──────────────────────────────────────── #
        exp_ctry_totals: dict[str, float] = {}
        for (_, c), v in raw_exports.items():
            exp_ctry_totals[c] = exp_ctry_totals.get(c, 0.0) + v

        exp_prod_totals: dict[str, float] = {}
        for (p, _), v in raw_exports.items():
            exp_prod_totals[p] = exp_prod_totals.get(p, 0.0) + v

        sig_ec = {c for c, v in exp_ctry_totals.items() if v >= exp_threshold}
        has_other_ec = len(sig_ec) < len(exp_ctry_totals)
        sig_ep = sorted(
            p for p, v in exp_prod_totals.items() if v >= exp_threshold
        )
        has_other_ep = len(sig_ep) < len(exp_prod_totals)

        ic_sorted = sorted(sig_ic)
        ec_sorted = sorted(sig_ec)

        # ── Node index layout ────────────────────────────────────────────── #
        # [imp_countries | Other_IC | imp_products | Other_IP |
        #  focal | exp_products | Other_EP | exp_countries | Other_EC]
        ic_base = 0
        ic_idx = {c: ic_base + i for i, c in enumerate(ic_sorted)}
        n_ic = len(ic_sorted)
        other_ic_idx = n_ic if has_other_ic else None

        ip_base = n_ic + (1 if has_other_ic else 0)
        ip_idx = {p: ip_base + i for i, p in enumerate(sig_ip)}
        n_ip = len(sig_ip)
        other_ip_idx = ip_base + n_ip if has_other_ip else None

        focal_idx = ip_base + n_ip + (1 if has_other_ip else 0)

        ep_base = focal_idx + 1
        ep_idx = {p: ep_base + i for i, p in enumerate(sig_ep)}
        n_ep = len(sig_ep)
        other_ep_idx = ep_base + n_ep if has_other_ep else None

        ec_base = ep_base + n_ep + (1 if has_other_ep else 0)
        ec_idx = {c: ec_base + i for i, c in enumerate(ec_sorted)}
        n_ec = len(ec_sorted)
        other_ec_idx = ec_base + n_ec if has_other_ec else None

        # "Other" bucket totals (for label annotations)
        other_ic_total = sum(
            v for (_, c), v in raw_imports.items() if c not in sig_ic
        )
        other_ip_total = sum(
            v for (p, _), v in raw_imports.items() if p not in set(sig_ip)
        )
        other_ep_total = sum(
            v for (p, _), v in raw_exports.items() if p not in set(sig_ep)
        )
        other_ec_total = sum(
            v for (_, c), v in raw_exports.items() if c not in sig_ec
        )

        imp_product_colors = {p: _product_color(p) for p in sig_ip}
        exp_product_colors = {p: _product_color(p) for p in sig_ep}

        # ── Node lists ───────────────────────────────────────────────────── #
        node_labels = (
            ic_sorted
            + ([_OTHER_LABEL] if has_other_ic else [])
            + [_product_label(p) for p in sig_ip]
            + ([_OTHER_LABEL] if has_other_ip else [])
            + [country]
            + [_product_label(p) for p in sig_ep]
            + ([_OTHER_LABEL] if has_other_ep else [])
            + ec_sorted
            + ([_OTHER_LABEL] if has_other_ec else [])
        )
        node_totals = (
            [imp_ctry_totals[c] for c in ic_sorted]
            + ([other_ic_total] if has_other_ic else [])
            + [imp_prod_totals[p] for p in sig_ip]
            + ([other_ip_total] if has_other_ip else [])
            + [max(total_imports, total_exports)]
            + [exp_prod_totals[p] for p in sig_ep]
            + ([other_ep_total] if has_other_ep else [])
            + [exp_ctry_totals[c] for c in ec_sorted]
            + ([other_ec_total] if has_other_ec else [])
        )
        node_colors = (
            ["#5577AA"] * n_ic
            + ([_OTHER_COLOR] if has_other_ic else [])
            + [imp_product_colors[p] for p in sig_ip]
            + ([_OTHER_COLOR] if has_other_ip else [])
            + ["#444444"]
            + [exp_product_colors[p] for p in sig_ep]
            + ([_OTHER_COLOR] if has_other_ep else [])
            + ["#AA5555"] * n_ec
            + ([_OTHER_COLOR] if has_other_ec else [])
        )

        node_labels_ann = [
            f"{lbl} ({_fmt_musd(t)})"
            for lbl, t in zip(node_labels, node_totals)
        ]
        # Override focal node label to show both sides and balance
        balance_word = "Surplus" if balance >= 0 else "Deficit"
        node_labels_ann[focal_idx] = (
            f"{country} "
            f"(In {_fmt_musd(total_imports)} / Out {_fmt_musd(total_exports)}"
            f" / {balance_word} {_fmt_musd(abs(balance))})"
        )

        # ── Build links ──────────────────────────────────────────────────── #
        link_acc: dict[tuple[int, int, str], float] = {}

        # Import side: import_country → import_product → focal
        for (product, c), value in raw_imports.items():
            ic_node = ic_idx.get(c, other_ic_idx)
            if product in ip_idx:
                ip_node = ip_idx[product]
                lp = "imp_" + product
            else:
                ip_node = other_ip_idx
                lp = "imp_" + _OTHER_LABEL
            k1 = (ic_node, ip_node, lp)
            k2 = (ip_node, focal_idx, lp)
            link_acc[k1] = link_acc.get(k1, 0.0) + value
            link_acc[k2] = link_acc.get(k2, 0.0) + value

        # Export side: focal → export_product → export_country
        for (product, c), value in raw_exports.items():
            ec_node = ec_idx.get(c, other_ec_idx)
            if product in ep_idx:
                ep_node = ep_idx[product]
                lp = "exp_" + product
            else:
                ep_node = other_ep_idx
                lp = "exp_" + _OTHER_LABEL
            k1 = (focal_idx, ep_node, lp)
            k2 = (ep_node, ec_node, lp)
            link_acc[k1] = link_acc.get(k1, 0.0) + value
            link_acc[k2] = link_acc.get(k2, 0.0) + value

        sources, targets, values, link_colors = [], [], [], []
        for (src, tgt, lp), value in link_acc.items():
            sources.append(src)
            targets.append(tgt)
            values.append(value)
            if lp.startswith("imp_"):
                code = lp[4:]
                color = imp_product_colors.get(code, _OTHER_COLOR)
            else:
                code = lp[4:]
                color = exp_product_colors.get(code, _OTHER_COLOR)
            link_colors.append(_rgba(color, 0.45))

        # ── Title ────────────────────────────────────────────────────────── #
        pct = int(other_threshold * 100)
        balance_str = (
            f"Trade {'Surplus' if balance >= 0 else 'Deficit'}: "
            f"{_fmt_musd(abs(balance))}"
        )
        title = (
            f"Trade Flows Through {country} ({year})  ·  {balance_str}<br>"
            f"<sup>Import sources → Imports → {country} → Exports → Export destinations"
            f"  ·  flows &lt;{pct}% of side total grouped as 'Other'</sup>"
        )

        safe = country.replace(" ", "_")
        png_path = os.path.join(
            os.path.normpath(_IMAGES_DIR),
            f"sankey_combined_{safe}_{year}.png",
        )

        fig = go.Figure(
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=15,
                    thickness=20,
                    label=node_labels_ann,
                    color=node_colors,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=link_colors,
                ),
            )
        )
        fig.update_layout(title_text=title, font_size=11)

        images_dir = os.path.normpath(_IMAGES_DIR)
        os.makedirs(images_dir, exist_ok=True)
        fig.write_image(png_path, width=2400, height=1000, scale=2)
        os.system(f"open {png_path}")
        return fig
