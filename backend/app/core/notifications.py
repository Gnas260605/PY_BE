import logging
import httpx
from smtplib import SMTP
from email.message import EmailMessage
from app.core.config import get_settings

logger = logging.getLogger(__name__)

async def send_telegram_message(message: str) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("TELEGRAM_CONFIG_MISSING")
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info("TELEGRAM_NOTIFICATION_SENT")
    except Exception as exc:
        logger.error("TELEGRAM_NOTIFICATION_FAILED error_type=%s", type(exc).__name__)

def send_email_notification(to_email: str, subject: str, content: str) -> None:
    settings = get_settings()
    if not all([settings.smtp_host, settings.smtp_port, settings.smtp_user, settings.smtp_password, settings.smtp_from]):
        logger.warning("SMTP_CONFIG_MISSING")
        return

    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    try:
        with SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
            logger.info("EMAIL_NOTIFICATION_SENT recipient=%s", to_email)
    except Exception as exc:
        logger.error("EMAIL_NOTIFICATION_FAILED error_type=%s", type(exc).__name__)
