from io import BytesIO
from xml.sax.saxutils import escape

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


def generate_activity_report_pdf(
    report: dict,
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
            f"<b>{escape(business.name)}</b>",
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
            "<b>RAPPORT D'ACTIVITÉ</b>",
            styles["Heading1"],
        )
    )

    story.append(
        Paragraph(
            escape(report["period_label"]),
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 6 * mm))

    data = [
        ["Indicateur", "Valeur"],
        [
            "Chiffre d'affaires",
            f'{report["total_sales"]:,.0f} FCFA',
        ],
        [
            "Dépenses",
            f'{report["total_expenses"]:,.0f} FCFA',
        ],
        [
            "Remboursements de dettes",
            f'{report["total_debt_payments"]:,.0f} FCFA',
        ],
        [
            "Flux net",
            f'{report["net_cash_flow"]:,.0f} FCFA',
        ],
        [
            "Marge brute",
            f'{report["gross_margin"]:,.0f} FCFA',
        ],
        [
            "Encours de dettes",
            f'{report["outstanding_debt"]:,.0f} FCFA',
        ],
        [
            "Valeur stock à l'achat",
            f'{report["stock_purchase_value"]:,.0f} FCFA',
        ],
        [
            "Valeur stock à la vente",
            f'{report["stock_selling_value"]:,.0f} FCFA',
        ],
    ]

    table = Table(
        data,
        colWidths=[
            100 * mm,
            65 * mm,
        ],
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
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
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
                    "ALIGN",
                    (1, 1),
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

    story.append(table)
    story.append(Spacer(1, 8 * mm))

    operations = [
        ["Activité", "Nombre"],
        ["Ventes", str(report["sales_count"])],
        ["Dépenses", str(report["expenses_count"])],
        ["Nouvelles dettes", str(report["debts_count"])],
        [
            "Remboursements",
            str(report["debt_payments_count"]),
        ],
    ]

    operations_table = Table(
        operations,
        colWidths=[
            100 * mm,
            65 * mm,
        ],
    )

    operations_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
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
                    "ALIGN",
                    (1, 1),
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

    story.append(operations_table)
    story.append(Spacer(1, 8 * mm))

    low_stock = report["low_stock_products"]

    if low_stock:
        low_stock_text = (
            "<b>Alertes stock :</b> "
            + ", ".join(escape(item) for item in low_stock)
        )
    else:
        low_stock_text = (
            "<b>Alertes stock :</b> "
            "Aucune alerte."
        )

    story.append(
        Paragraph(
            low_stock_text,
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            f"Document généré par JËFAL — "
            f"{escape(business.name)}",
            styles["Normal"],
        )
    )

    document.build(story)

    return buffer.getvalue()
