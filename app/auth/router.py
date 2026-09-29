from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth_service import authenticate_user, login_user
from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings
from app.database.dependencies import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])
failed_logins: dict[str, deque[float]] = defaultdict(deque)


def login_allowed(key: str) -> bool:
    now = time.monotonic()
    attempts = failed_logins[key]
    while attempts and now - attempts[0] > settings.LOGIN_RATE_WINDOW_SECONDS:
        attempts.popleft()
    return len(attempts) < settings.LOGIN_RATE_LIMIT


def record_login_failure(key: str) -> None:
    failed_logins[key].append(time.monotonic())


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def set_auth_cookies(response: Response, access_token: str, refresh_token: str | None = None) -> None:
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    response.set_cookie(
        "csrf_token",
        secrets.token_urlsafe(32),
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    if refresh_token is not None:
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            path="/auth",
        )


@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    key = f"{request.client.host if request.client else 'unknown'}:{form_data.username.strip()}"
    if not login_allowed(key):
        raise HTTPException(status_code=429, detail="Trop de tentatives. Réessayez plus tard.")
    user = authenticate_user(db, form_data.username.strip(), form_data.password)
    if user is None:
        record_login_failure(key)
        raise HTTPException(status_code=401, detail="Téléphone ou mot de passe incorrect.")
    failed_logins.pop(key, None)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=token_hash(refresh_token),
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    db.commit()
    if request.headers.get("X-Client-Type", "").lower() in {"mobile", "android", "ios"}:
        return JSONResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        })
    response = Response(content='{"token_type":"bearer"}', media_type="application/json")
    set_auth_cookies(response, access_token, refresh_token)
    return response


@router.post("/refresh")
def refresh(
    request: Request,
    body: dict | None = Body(default=None),
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if request.headers.get("X-Client-Type", "").lower() in {"mobile", "android", "ios"}:
        refresh_token = body.get("refresh_token") if body else None
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token manquant.")
    if not isinstance(refresh_token, str):
        raise HTTPException(status_code=401, detail="Refresh token invalide.")
    try:
        payload = decode_refresh_token(refresh_token)
        user_id = int(payload["sub"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Refresh token invalide.")
    stored = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash(refresh_token),
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    ).first()
    if stored is None or stored.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token invalide.")
    stored.revoked_at = datetime.utcnow()
    new_refresh = create_refresh_token(user_id)
    db.add(RefreshToken(
        user_id=user_id,
        token_hash=token_hash(new_refresh),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    db.commit()
    if request.headers.get("X-Client-Type", "").lower() in {"mobile", "android", "ios"}:
        return JSONResponse({
            "access_token": create_access_token(user_id),
            "refresh_token": new_refresh,
            "token_type": "bearer",
        })
    response = Response(content='{"token_type":"bearer"}', media_type="application/json")
    set_auth_cookies(response, create_access_token(user_id), new_refresh)
    return response


@router.post("/logout")
def logout(response: Response, refresh_token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if refresh_token:
        stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash(refresh_token)).first()
        if stored is not None:
            stored.revoked_at = datetime.utcnow()
            db.commit()
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth")
    return {"message": "Déconnexion réussie."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
