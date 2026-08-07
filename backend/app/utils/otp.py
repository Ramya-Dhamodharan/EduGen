import hashlib
import hmac
import secrets
import time

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import redis

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 3 * 60  # 3 minutes
EMAIL_TTL_SECONDS = 24 * 60 * 60  # 1 day
MAX_ATTEMPTS = 3


def hash_otp(email: str, otp: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"{email}.{otp}".encode(),
        hashlib.sha256,
    ).hexdigest()


def create_otp() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


async def generate_otp(email: str) -> str:
    key = f"email_otp:{email}"

    data = await redis.hgetall(key)

    # Existing record
    if data:
        attempts = int(data.get("attempts", "0"))

        # User exhausted attempts
        if attempts >= MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum OTP attempts reached. Try again after 24 hours.",
            )

    otp = create_otp()

    await redis.hset(
        key,
        mapping={
            "otp_hash": hash_otp(email, otp),
            "attempts": "0",
            "created_at": str(int(time.time())),
        },
    )

    # Set TTL only for a new key.
    if not data:
        await redis.expire(key, EMAIL_TTL_SECONDS)

    return otp


async def verify_otp(email: str, otp: str) -> bool:
    key = f"email_otp:{email}"

    data = await redis.hgetall(key)

    if not data:
        return False

    attempts = int(data.get("attempts", "0"))

    # User is blocked
    if attempts >= MAX_ATTEMPTS:
        return False

    created_at = int(data["created_at"])

    # OTP expired
    if int(time.time()) - created_at > OTP_EXPIRY_SECONDS:
        return False

    # Correct OTP
    if hmac.compare_digest(
        data["otp_hash"],
        hash_otp(email, otp),
    ):
        # Remove only OTP information.
        # The key remains until the 1-day TTL expires.
        await redis.hdel(
            key,
            "otp_hash",
            "created_at",
        )
        return True

    # Wrong OTP
    attempts = await redis.hincrby(
        key,
        "attempts",
        1,
    )

    if attempts >= MAX_ATTEMPTS:
        return False

    return False


async def get_remaining_otp_time(email: str) -> int:
    """
    Returns remaining OTP lifetime in seconds.
    """

    key = f"email_otp:{email}"

    created_at = await redis.hget(
        key,
        "created_at",
    )

    if not created_at:
        return 0

    elapsed = int(time.time()) - int(created_at)

    remaining = OTP_EXPIRY_SECONDS - elapsed

    return max(0, remaining)


async def get_remaining_email_time(email: str) -> int:
    """
    Returns remaining Redis key lifetime.
    """

    return await redis.ttl(f"email_otp:{email}")
