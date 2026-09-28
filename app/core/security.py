from pwdlib import PasswordHash
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


password_hash = PasswordHash.recommended()
fernet = Fernet(settings.ENCRYPTION_KEY)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def normalize_phone(phone: str) -> str:
    return "".join(phone.split())


def encrypt_phone(phone: str) -> str:
    return fernet.encrypt(normalize_phone(phone).encode()).decode()


def decrypt_phone(value: str) -> str:
    try:
        return fernet.decrypt(value.encode()).decode()
    except InvalidToken as error:
        raise ValueError("Unable to decrypt phone number") from error
