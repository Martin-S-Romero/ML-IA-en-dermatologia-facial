import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_GMAIL_USER = os.getenv("GMAIL_USER", "")
_GMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD", "")
_FRONTEND   = os.getenv("FRONTEND_URL", "http://localhost:3000")


def send_password_reset_email(to_email: str, token: str) -> bool:
    reset_url = f"{_FRONTEND}?reset_token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Restablecer contraseña - SkinAI"
    msg["From"]    = f"SkinAI <{_GMAIL_USER}>"
    msg["To"]      = to_email

    html = f"""
    <div style="font-family:'DM Sans',sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#FAF8F3;border-radius:16px;">
      <h2 style="font-family:serif;color:#233D30;margin-bottom:8px;">Restablecer contraseña</h2>
      <p style="color:#5A6474;font-size:14px;line-height:1.6;margin-bottom:24px;">
        Hemos recibido una solicitud para restablecer la contraseña de tu cuenta SkinAI.
        Haz clic en el botón para crear una nueva contraseña.
      </p>
      <a href="{reset_url}"
         style="display:inline-block;background:#233D30;color:#FAF8F3;padding:12px 28px;
                border-radius:999px;text-decoration:none;font-weight:600;font-size:14px;margin-bottom:24px;">
        Restablecer contraseña
      </a>
      <p style="color:#9AA4B0;font-size:12px;line-height:1.5;">
        Este enlace expirará en <strong>1 hora</strong>.<br>
        Si no solicitaste este cambio, puedes ignorar este correo.
      </p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(_GMAIL_USER, _GMAIL_PASS)
            server.sendmail(_GMAIL_USER, to_email, msg.as_string())
        return True
    except Exception:
        return False
