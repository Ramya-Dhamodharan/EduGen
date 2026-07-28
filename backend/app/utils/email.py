import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def is_smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def _print_otp_to_terminal(to_email: str, otp: str, reason: str = "SMTP not configured") -> None:
    print("=" * 60)
    print(f"  [DEV MODE - {reason}]")
    print(f"  Password reset OTP for {to_email}: {otp}")
    print(f"  (valid for 5 minutes)")
    print("=" * 60)


def send_otp_email(to_email: str, otp: str) -> None:
    """Email the OTP if SMTP is configured in .env; otherwise (or on
    failure) print it to the terminal so development is never blocked."""
    if not is_smtp_configured():
        _print_otp_to_terminal(to_email, otp)
        return

    sender = settings.SMTP_FROM or settings.SMTP_USER
    msg = EmailMessage()
    msg["Subject"] = f"{settings.APP_NAME} - Password Reset Code"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"Hello,\n\nYour password reset code is: {otp}\n\n"
        f"This code is valid for 5 minutes. If you did not request a "
        f"password reset, you can safely ignore this email.\n\n- {settings.APP_NAME}"
    )

    try:
        if settings.SMTP_USE_TLS:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT,
                                  context=ssl.create_default_context(), timeout=15) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        logger.info("OTP email sent to %s", to_email)
    except Exception as exc:
        logger.error("Failed to send OTP email to %s: %s", to_email, exc)
        _print_otp_to_terminal(to_email, otp, reason=f"SMTP send failed: {exc}")
