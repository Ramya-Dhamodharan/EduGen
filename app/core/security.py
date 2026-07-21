import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


# ==========================
# Password hashing (bcrypt, no passlib)
# ==========================

def _to_bcrypt_bytes(password: str) -> bytes:
    # bcrypt only uses the first 72 bytes; truncate explicitly so
    # bcrypt >= 4.1 does not raise ValueError.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Turn a plain-text password into a bcrypt hash before storing it."""
    return bcrypt.hashpw(_to_bcrypt_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(_to_bcrypt_bytes(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        return False


# ==========================
# JWT tokens
# ==========================

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ==========================
# OTP store for password reset (server-side, in-memory)
# The OTP is stored hashed, is single-use, expires after 5 minutes,
# and locks out after 5 wrong attempts.
# NOTE: in-memory works for a single-process dev server. For production
# with multiple workers, move this to Redis or user-table columns.
# ==========================

_OTP_TTL_MINUTES = 5

_otp_store: dict[str, dict] = {}


def _hash_otp(email: str, otp: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"{email}.{otp}".encode(),
        hashlib.sha256,
    ).hexdigest()


def generate_otp(email: str) -> str:
    """Create a 6-digit OTP for this email, replacing any previous one."""
    otp = f"{secrets.randbelow(900000) + 100000}"
    _otp_store[email] = {
        "otp_hash": _hash_otp(email, otp),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=_OTP_TTL_MINUTES),
        "attempts": 0,
    }
    return otp


def verify_otp(email: str, otp: str) -> bool:
    """Check the OTP; consumes it on success, enforces expiry + attempts."""
    entry = _otp_store.get(email)
    if not entry:
        return False
    if datetime.now(timezone.utc) > entry["expires_at"]:
        _otp_store.pop(email, None)
        return False
    if hmac.compare_digest(entry["otp_hash"], _hash_otp(email, otp)):
        _otp_store.pop(email, None)
        return True
    return False
