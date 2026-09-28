from pathlib import Path
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph


def generate_invoice_pdf(sale) -> bytes:
    """
    Génère une facture PDF à partir d'une vente existante.

    Les informations de l'activité sont récupérées depuis sale.business.
    """

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    business = sale.business

    # ---------------------------------------------------------
    # En-tête de l'entreprise
    # ---------------------------------------------------------

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(
        20 * mm,
        height - 25 * mm,
        business.name,
    )

    pdf.setFont("Helvetica", 10)

    if business.sector:
        pdf.drawString(
            20 * mm,
            height - 32 * mm,
            business.sector,
        )

    if business.location:
        pdf.drawString(
            20 * mm,
            height - 38 * mm,
            business.location,
        )

    # ---------------------------------------------------------
    # Titre facture
    # ---------------------------------------------------------

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawRightString(
        width - 20 * mm,
        height - 25 * mm,
        "FACTURE",
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(
        width - 20 * mm,
        height - 32 * mm,
        f"N° FAC-{sale.id:06d}",
    )

    sale_date = (
        sale.sold_at.strftime("%d/%m/%Y")
        if sale.sold_at
        else ""
    )

    pdf.drawRightString(
        width - 20 * mm,
        height - 38 * mm,
        f"Date : {sale_date}",
    )

    # ---------------------------------------------------------
    # Ligne de séparation
    # ---------------------------------------------------------

    y = height - 50 * mm

    pdf.line(
        20 * mm,
        y,
        width - 20 * mm,
        y,
    )

    # ---------------------------------------------------------
    # Tableau des produits
    # ---------------------------------------------------------

    y -= 12 * mm

    col_product = 20 * mm
    col_quantity = 105 * mm
    col_unit_price = 135 * mm
    col_total = 175 * mm

    pdf.setFont("Helvetica-Bold", 9)

    pdf.drawString(
        col_product,
        y,
        "Produit",
    )

    pdf.drawString(
        col_quantity,
        y,
        "Qté",
    )

    pdf.drawString(
        col_unit_price,
        y,
        "Prix unitaire",
    )

    pdf.drawRightString(
        width - 20 * mm,
        y,
        "Total",
    )

    y -= 5 * mm

    pdf.line(
        20 * mm,
        y,
        width - 20 * mm,
        y,
    )

    y -= 8 * mm

    pdf.setFont("Helvetica", 9)

    for item in sale.items:
        product_name = item.product.name
        quantity = f"{float(item.quantity):g}"
        unit = item.unit
        unit_price = f"{float(item.unit_price):,.0f} FCFA"
        subtotal = f"{float(item.subtotal):,.0f} FCFA"

        pdf.drawString(
            col_product,
            y,
            product_name[:45],
        )

        pdf.drawString(
            col_quantity,
            y,
            f"{quantity} {unit}",
        )

        pdf.drawString(
            col_unit_price,
            y,
            unit_price,
        )

        pdf.drawRightString(
            width - 20 * mm,
            y,
            subtotal,
        )

        y -= 8 * mm

        if y < 40 * mm:
            pdf.showPage()
            y = height - 25 * mm
            pdf.setFont("Helvetica", 9)

    # ---------------------------------------------------------
    # Total
    # ---------------------------------------------------------

    y -= 5 * mm

    pdf.line(
        120 * mm,
        y,
        width - 20 * mm,
        y,
    )

    y -= 10 * mm

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(
        120 * mm,
        y,
        "TOTAL",
    )

    pdf.drawRightString(
        width - 20 * mm,
        y,
        f"{float(sale.total_amount):,.0f} FCFA",
    )

    # ---------------------------------------------------------
    # Mode de paiement
    # ---------------------------------------------------------

    y -= 10 * mm

    pdf.setFont("Helvetica", 9)

    payment_method = sale.payment_method or "Non précisé"

    pdf.drawString(
        120 * mm,
        y,
        f"Paiement : {payment_method}",
    )

    # ---------------------------------------------------------
    # Pied de page
    # ---------------------------------------------------------

    pdf.setFont("Helvetica", 8)

    pdf.drawCentredString(
        width / 2,
        15 * mm,
        f"Merci de votre confiance — {business.name}",
    )

    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()
