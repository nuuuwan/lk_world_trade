import os

import plotly.graph_objects as go

from ._trade_info import TradeInfo

_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "images")

_PALETTE = [
    "#636EFA",
    "#EF553B",
    "#00CC96",
    "#AB63FA",
    "#FFA15A",
    "#19D3F3",
    "#FF6692",
    "#B6E880",
    "#FF97FF",
    "#FECB52",
    "#1F77B4",
    "#FF7F0E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#8C564B",
]

_OTHER_LABEL = "Other"
_OTHER_COLOR = "#AAAAAA"


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a 6-digit hex colour + alpha to an rgba() string."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


class Sankey:
    """Sankey diagram visualisation of trade flows.

    The diagram shows three levels, all links coloured by product group:

        exporter_country  →  product_group  →  importer

    Countries whose total trade is below ``other_threshold`` × grand total are
    collapsed into a single "Other" node.
    """

    @staticmethod
    def draw(
        importer: str,
        year: int,
        other_threshold: float = 0.02,
    ) -> go.Figure:
        """Build and display a Sankey diagram of all imports.

        Args:
            importer: Importing country name (e.g. 'Sri Lanka').
            year: Reference year (e.g. 2022).
            other_threshold: Fraction of grand total below which a country is
                grouped into "Other". Default 0.02 (2 %).

        Returns:
            A ``plotly.graph_objects.Figure`` that is shown in the browser and
            saved as a PNG to the ``images/`` directory at the project root.
        """
        trade_info = TradeInfo.get(importer=importer, year=year)

        # ------------------------------------------------------------------ #
        # 1. Flatten raw flows: {(product, country): value}                   #
        # ------------------------------------------------------------------ #
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

        threshold_value = other_threshold * grand_total

        # ------------------------------------------------------------------ #
        # 2. Determine significant countries; rest → "Other"                  #
        # ------------------------------------------------------------------ #
        country_totals: dict[str, float] = {}
        for (_, country), value in raw.items():
            country_totals[country] = country_totals.get(country, 0.0) + value

        significant = {
            c for c, v in country_totals.items() if v >= threshold_value
        }
        has_other = len(significant) < len(country_totals)

        # ------------------------------------------------------------------ #
        # 3. Build node index                                                  #
        # Node layout:                                                         #
        #   0 … C-1   : significant exporter countries  (left)                #
        #   C         : "Other" country node  (left, only if needed)          #
        #   next P    : product groups  (middle)                               #
        #   last      : importer  (right)                                      #
        # ------------------------------------------------------------------ #
        product_groups = sorted(trade_info.data.keys())
        countries_sorted = sorted(significant)

        product_colors = {
            p: _PALETTE[i % len(_PALETTE)]
            for i, p in enumerate(product_groups)
        }

        c_idx = {c: i for i, c in enumerate(countries_sorted)}
        other_idx = len(countries_sorted) if has_other else None
        p_base = len(countries_sorted) + (1 if has_other else 0)
        p_idx = {p: p_base + i for i, p in enumerate(product_groups)}
        importer_idx = p_base + len(product_groups)

        node_labels = (
            countries_sorted
            + ([_OTHER_LABEL] if has_other else [])
            + product_groups
            + [importer]
        )
        node_colors = (
            ["#888888"] * len(countries_sorted)
            + ([_OTHER_COLOR] if has_other else [])
            + [product_colors[p] for p in product_groups]
            + ["#444444"]
        )

        # ------------------------------------------------------------------ #
        # 4. Build links                                                       #
        #                                                                      #
        # Both legs (exporter→product and product→importer) are coloured by   #
        # product so every link inherits the product's colour end-to-end.     #
        # ------------------------------------------------------------------ #
        # Accumulate into (src, tgt, product) → value to merge parallel edges
        link_acc: dict[tuple[int, int, str], float] = {}

        for (product, country), value in raw.items():
            country_node = c_idx.get(country, other_idx)  # significant or Other

            # Leg 1: exporter/Other → product
            k1 = (country_node, p_idx[product], product)
            link_acc[k1] = link_acc.get(k1, 0.0) + value

            # Leg 2: product → importer  (same product colour)
            k2 = (p_idx[product], importer_idx, product)
            link_acc[k2] = link_acc.get(k2, 0.0) + value

        sources, targets, values, link_colors = [], [], [], []
        for (src, tgt, product), value in link_acc.items():
            sources.append(src)
            targets.append(tgt)
            values.append(value)
            link_colors.append(_rgba(product_colors[product], 0.45))

        # ------------------------------------------------------------------ #
        # 5. Assemble figure                                                   #
        # ------------------------------------------------------------------ #
        fig = go.Figure(
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=15,
                    thickness=20,
                    label=node_labels,
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
        pct = int(other_threshold * 100)
        fig.update_layout(
            title_text=(
                f"Trade Flows into {importer} ({year})<br>"
                f"<sup>Exporter → Product group → Importer (USD) "
                f"· flows &lt;{pct}% of total grouped as 'Other'</sup>"
            ),
            font_size=11,
        )

        images_dir = os.path.normpath(_IMAGES_DIR)
        os.makedirs(images_dir, exist_ok=True)
        safe_importer = importer.replace(" ", "_")
        png_path = os.path.join(
            images_dir, f"sankey_{safe_importer}_{year}.png"
        )
        fig.write_image(png_path, width=1600, height=900, scale=2)

        os.system(f"open {png_path}")
        return fig
