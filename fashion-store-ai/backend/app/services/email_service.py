import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger("fashion_store.email")


def generate_otp_html(otp: str, purpose: str = "register", email: str = "") -> str:
    """Tạo giao diện email HTML chuyên nghiệp cho Fashion Store AI."""
    purpose_title = "XÁC THỰC ĐĂNG KÝ TÀI KHOẢN" if purpose == "register" else "KHÔI PHỤC MẬT KHẨU"
    purpose_desc = (
        "Cảm ơn bạn đã lựa chọn Fashion Store AI. Dưới đây là mã xác thực OTP dùng để hoàn tất đăng ký tài khoản của bạn:"
        if purpose == "register"
        else "Bạn vừa gửi yêu cầu khôi phục mật khẩu tài khoản tại Fashion Store AI. Dưới đây là mã OTP của bạn:"
    )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      margin: 0;
      padding: 0;
      color: #1e293b;
    }}
    .email-container {{
      max-width: 580px;
      margin: 30px auto;
      background: #ffffff;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #0f766e, #14b8a6);
      padding: 32px 24px;
      text-align: center;
      color: #ffffff;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 1px;
      font-weight: 800;
    }}
    .header p {{
      margin: 6px 0 0;
      font-size: 13px;
      opacity: 0.9;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .content {{
      padding: 32px 28px;
      line-height: 1.6;
    }}
    .otp-box {{
      margin: 28px 0;
      text-align: center;
      background: #f0fdfa;
      border: 2px dashed #0d9488;
      border-radius: 12px;
      padding: 20px;
    }}
    .otp-code {{
      font-size: 36px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #0f766e;
      font-family: monospace;
      margin: 4px 0;
    }}
    .otp-hint {{
      font-size: 13px;
      color: #64748b;
      margin-top: 8px;
    }}
    .warning {{
      background: #fffbeb;
      border-left: 4px solid #f59e0b;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 13px;
      color: #92400e;
      margin-top: 24px;
    }}
    .footer {{
      background: #f8fafc;
      padding: 20px 24px;
      text-align: center;
      border-top: 1px solid #e2e8f0;
      font-size: 12px;
      color: #94a3b8;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>FASHION STORE AI</h1>
      <p>AI Shopping Boutique & Virtual Stylist</p>
    </div>
    <div class="content">
      <h2 style="font-size: 18px; color: #0f172a; margin-top: 0;">{purpose_title}</h2>
      <p>{purpose_desc}</p>
      
      <div class="otp-box">
        <div style="font-size: 12px; text-transform: uppercase; color: #0d9488; font-weight: 700; margin-bottom: 4px;">
          MÃ XÁC THỰC OTP
        </div>
        <div class="otp-code">{otp}</div>
        <div class="otp-hint">⏱️ Mã có hiệu lực trong vòng <strong>1 phút (60 giây)</strong></div>
      </div>

      <div class="warning">
        🔒 <strong>Bảo mật:</strong> Vui lòng tuyệt đối không chia sẻ mã này cho bất kỳ ai. Fashion Store AI sẽ không bao giờ chủ động yêu cầu bạn cung cấp mã xác thực.
      </div>

      <p style="margin-top: 24px; font-size: 13px; color: #64748b;">
        Nếu bạn không thực hiện yêu cầu này, bạn có thể yên tâm bỏ qua email này.
      </p>
    </div>
    <div class="footer">
      © 2026 Fashion Store AI. Hệ thống thời trang thông minh tích hợp AI Stylist.<br/>
      Email gửi tự động, vui lòng không phản hồi thư này.
    </div>
  </div>
</body>
</html>"""


class EmailService:
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Gửi email qua SMTP chuẩn. Bắt buộc có SMTP cấu hình hợp lệ để gửi đến email người nhận."""
        settings = get_settings()
        if not settings.smtp_host or not settings.smtp_user:
            err = "Hệ thống chưa được cấu hình SMTP_HOST và SMTP_USER trong file backend/.env. Vui lòng thêm tài khoản Gmail và Mật khẩu ứng dụng để gửi email thật."
            logger.error(f"[EMAIL ERROR] {err}")
            return False, err

        try:
            msg = MIMEMultipart("alternative")
            from_addr = settings.smtp_from_email or settings.smtp_user
            msg["From"] = f"{settings.smtp_from_name} <{from_addr}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if text_content:
                msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            if settings.smtp_port == 465:
                server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15)
            else:
                server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)
                if settings.smtp_tls:
                    server.starttls()

            if settings.smtp_password:
                clean_pw = settings.smtp_password.replace(" ", "").strip()
                server.login(settings.smtp_user.strip(), clean_pw)

            server.send_message(msg)
            server.quit()
            logger.info(f"Đã gửi email thành công tới {to_email}")
            return True, None
        except smtplib.SMTPAuthenticationError:
            err = "Tài khoản hoặc mật khẩu SMTP không đúng. Với Gmail, Google bắt buộc phải dùng 'Mật khẩu ứng dụng' (App Password gồm 16 chữ cái), không thể dùng mật khẩu đăng nhập Gmail thông thường."
            logger.error(f"[SMTP AUTH ERROR] {err}")
            return False, err
        except Exception as e:
            err_str = str(e)
            if "535" in err_str or "Username and Password not accepted" in err_str or "BadCredentials" in err_str:
                err = "Google từ chối mật khẩu (BadCredentials). Bạn cần tạo 'Mật khẩu ứng dụng' (App Password 16 chữ cái) trong tài khoản Google để dán vào SMTP_PASSWORD."
            elif "Connection unexpectedly closed" in err_str:
                err = "Kết nối SMTP bị đóng (thường do Google từ chối mật khẩu thông thường. Gmail bắt buộc dùng Mật khẩu ứng dụng 16 ký tự)."
            else:
                err = f"Lỗi gửi email SMTP: {err_str}"
            logger.error(f"Lỗi khi gửi email qua SMTP tới {to_email}: {err}")
            return False, err

    @staticmethod
    def send_otp_email(to_email: str, otp: str, purpose: str = "register") -> dict:
        """Gửi mã OTP xác thực qua email cho người dùng."""
        subject = (
            "[Fashion Store AI] Mã OTP xác thực đăng ký tài khoản"
            if purpose == "register"
            else "[Fashion Store AI] Mã OTP khôi phục mật khẩu"
        )
        html_body = generate_otp_html(otp, purpose=purpose, email=to_email)
        text_body = f"Mã xác thực OTP Fashion Store AI của bạn là: {otp}. Mã có hiệu lực trong 1 phút (60 giây). Vui lòng không chia sẻ mã này."

        success, error = EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
        )

        return {
            "success": success,
            "error": error,
            "to_email": to_email,
        }

