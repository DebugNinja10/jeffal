from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.routers.business import router as business_router
from app.routers.product import router as product_router
from app.routers.user import router as user_router
from app.routers.sale import router as sale_router
from app.routers.expense import router as expense_router
from app.routers.summary import router as summary_router
from app.routers.debt import router as debt_router

app = FastAPI(
    title="JËFAL API",
    description="API backend de JËFAL",
    version="0.1.0",
)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(business_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(expense_router)
app.include_router(summary_router)
app.include_router(debt_router)
