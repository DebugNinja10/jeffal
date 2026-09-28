from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Paragraph,
)


def generate_inventory_pdf(
    inventory: dict,
    business,
) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            f"<b>{business.name}</b>",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            f"{business.sector} — "
            f"{business.location or ''}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            "<b>INVENTAIRE</b>",
            styles["Heading1"],
        )
    )

    story.append(
        Paragraph(
            inventory["period_label"],
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 6 * mm))

    data = [
        [
            "Produit",
            "Stock",
            "Vendu",
            "CA",
            "Valeur stock vente",
        ]
    ]

    for item in inventory["items"]:
        data.append(
            [
                item["product_name"],
                f'{item["stock_quantity"]:.3f} '
                f'{item["stock_unit"]}',
                f'{item["quantity_sold"]:.3f}',
                f'{item["revenue"]:,.0f} FCFA',
                f'{item["stock_selling_value"]:,.0f} FCFA',
            ]
        )

    table = Table(
        data,
        colWidths=[
            42 * mm,
            32 * mm,
            22 * mm,
            35 * mm,
            42 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 8 * mm))

    totals = [
        [
            "CA de la période",
            f'{inventory["total_period_revenue"]:,.0f} FCFA',
        ],
        [
            "Valeur du stock à l'achat",
            f'{inventory["total_stock_purchase_value"]:,.0f} FCFA',
        ],
        [
            "Valeur du stock à la vente",
            f'{inventory["total_stock_selling_value"]:,.0f} FCFA',
        ],
    ]

    totals_table = Table(
        totals,
        colWidths=[
            95 * mm,
            70 * mm,
        ],
    )

    totals_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(totals_table)

    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            f"Document généré par JËFAL — "
            f"{business.name}",
            styles["Normal"],
        )
    )

    document.build(story)

    return buffer.getvalue()
