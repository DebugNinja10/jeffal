class ActivityReportResponseService:

    PERIOD_LABELS = {
        "day": "d'aujourd'hui",
        "week": "de la semaine",
        "month": "du mois",
    }

    def build_response(self, report: dict) -> str:
        period = report.get("period", "month")
        period_text = self.PERIOD_LABELS.get(
            period,
            "de la période",
        )

        total_sales = float(report.get("total_sales", 0))
        total_expenses = float(report.get("total_expenses", 0))
        total_debt_payments = float(
            report.get("total_debt_payments", 0)
        )
        net_cash_flow = float(
            report.get("net_cash_flow", 0)
        )
        sales_count = int(report.get("sales_count", 0))
        expenses_count = int(report.get("expenses_count", 0))
        outstanding_debt = float(
            report.get("outstanding_debt", 0)
        )

        return (
            f"Voici votre rapport {period_text}. "
            f"Votre chiffre d'affaires est de "
            f"{total_sales:,.0f} francs CFA. "
            f"Vous avez réalisé {sales_count} ventes "
            f"et {expenses_count} dépenses, "
            f"pour un total de {total_expenses:,.0f} francs CFA. "
            f"Les remboursements de dettes s'élèvent à "
            f"{total_debt_payments:,.0f} francs CFA. "
            f"Votre flux net est de "
            f"{net_cash_flow:,.0f} francs CFA. "
            f"Il vous reste "
            f"{outstanding_debt:,.0f} francs CFA "
            f"de dettes à recouvrer."
        )
