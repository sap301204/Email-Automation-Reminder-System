import os, email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
import asyncio

class Mailer:
    def __init__(self, host, port, username, password, use_tls=True, rate_limit_per_min=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.rate_limit_per_min = rate_limit_per_min
        self._sent_in_window = 0
        self._window_start = None

    async def send_html(self, from_name, from_email, to_email, subject, html, retry=1):
        msg = MIMEMultipart("alternative")
        msg["From"] = email.utils.formataddr((from_name, from_email))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            if self.use_tls:
                smtp = aiosmtplib.SMTP(hostname=self.host, port=int(self.port), use_tls=True, timeout=20)
            else:
                smtp = aiosmtplib.SMTP(hostname=self.host, port=int(self.port), start_tls=True, timeout=20)
            await smtp.connect()
            if self.username and self.password:
                await smtp.login(self.username, self.password)
            resp = await smtp.send_message(msg)
            await smtp.quit()
            return {"ok": True, "provider_msg_id": str(resp)}
        except Exception as e:
            if retry > 0:
                await asyncio.sleep(1)
                return await self.send_html(from_name, from_email, to_email, subject, html, retry=retry-1)
            return {"ok": False, "error": str(e)}
