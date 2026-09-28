from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ENCRYPTION_KEY: str
    GEMINI_API_KEY: str | None = None
    ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "jeffal-api"
    JWT_AUDIENCE: str = "jeffal-client"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "strict"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = Field(default_factory=list)
    LOGIN_RATE_LIMIT: int = 5
    LOGIN_RATE_WINDOW_SECONDS: int = 900
    MAX_TTS_TEXT_LENGTH: int = 2000
    MAX_AGENT_MESSAGE_LENGTH: int = 4000
    MAX_AUDIO_SIZE_BYTES: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def validate_security(self) -> None:
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must contain at least 32 characters")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES < 5:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES is too short")
        if self.ALGORITHM != "HS256":
            raise ValueError("Only HS256 is supported")
        if self.REFRESH_TOKEN_EXPIRE_DAYS < 1:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS is invalid")
        if self.COOKIE_SAMESITE not in {"strict", "lax", "none"}:
            raise ValueError("COOKIE_SAMESITE is invalid")
        if self.ENVIRONMENT not in {"development", "production", "test"}:
            raise ValueError("ENVIRONMENT is invalid")
        if self.ENVIRONMENT == "production" and not self.COOKIE_SECURE:
            raise ValueError("COOKIE_SECURE must be enabled in production")
        if self.LOGIN_RATE_LIMIT < 1 or self.LOGIN_RATE_WINDOW_SECONDS < 60:
            raise ValueError("Login rate limit is invalid")

    def model_post_init(self, __context: object) -> None:
        self.validate_security()


settings = Settings()
