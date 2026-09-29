from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.routers.business import router as business_router
from app.routers.product import router as product_router
from app.routers.user import router as user_router
from app.routers.sale import router as sale_router
from app.routers.expense import router as expense_router
from app.routers.summary import router as summary_router
from app.routers.debt import router as debt_router
from app.routers.agent import router as agent_router
from app.routers.voice import router as voice_router
from app.routers.inventory import router as inventory_router
from app.routers.activity_report import router as activity_report_router
from app.core.config import settings

app = FastAPI(
    title="JËFAL API",
    description="API backend de JËFAL",
    version="0.1.0",
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
    openapi_url=None if settings.ENVIRONMENT == "production" else "/openapi.json",
)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.cookies.get("access_token"):
            if request.url.path not in {"/auth/login"}:
                cookie_token = request.cookies.get("csrf_token")
                header_token = request.headers.get("X-CSRF-Token")
                if not cookie_token or cookie_token != header_token:
                    return JSONResponse({"detail": "CSRF token invalide."}, status_code=403)
        return await call_next(request)


app.add_middleware(CSRFMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(business_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(expense_router)
app.include_router(summary_router)
app.include_router(debt_router)
app.include_router(agent_router)
app.include_router(voice_router)
app.include_router(inventory_router)
app.include_router(activity_report_router)
