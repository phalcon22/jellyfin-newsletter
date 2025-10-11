import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

def generate_mail_mime(html: str, mime_from: str, subject: str) -> MIMEMultipart:
    # Create the message container
    mime = MIMEMultipart("related")
    mime["From"] = mime_from
    mime["Subject"] = subject

    # Alternative part (HTML + plain fallback)
    mime_alternative = MIMEMultipart("alternative")
    mime.attach(mime_alternative)

    mime_alternative.attach(MIMEText("Your email client does not support HTML.", "plain"))
    mime_alternative.attach(MIMEText(html, "html"))

    return mime

def send_email(smtp_host: str, smtp_email: str, smtp_password: str, to: list[str], mime: MIMEMultipart) -> None:
    with smtplib.SMTP(smtp_host, 587) as server:
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(mime, to_addrs=to)

    logger.info("✅ Email sent!")
