import os
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()


SMTP_EMAIL = os.getenv("SMTP_EMAIL") or ""
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or ""


def send_otp_email(
    receiver_email: str,
    username: str,
    otp: str
):
    # Read HTML email template
    template_path = Path("templates/otp_email.html")

    html_content = template_path.read_text(
        encoding="utf-8"
    )

    # Replace template placeholders
    html_content = html_content.replace(
        "{{ username }}",
        username
    )

    html_content = html_content.replace(
        "{{ otp }}",
        otp
    )

    # Create email
    message = MIMEMultipart("alternative")

    message["Subject"] = "Password Reset OTP"
    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email

    # Attach HTML template
    html_part = MIMEText(
        html_content,
        "html"
    )

    message.attach(html_part)

    # Connect to Gmail SMTP
    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        # Login using Gmail App Password
        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        # Send email
        server.sendmail(
            SMTP_EMAIL,
            receiver_email,
            message.as_string()
        )