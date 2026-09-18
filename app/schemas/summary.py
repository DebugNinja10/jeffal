from pydantic import BaseModel


class BusinessSummaryResponse(BaseModel):
    total_sales: float
    total_expenses: float
    net_cash_flow: float

    sales_count: int
    stock_value: float
    gross_margin: float

    low_stock_products: list[str]
