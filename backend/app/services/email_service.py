# app/services/email_service.py
"""Working Email service based on your previous successful implementation."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
import asyncio
from ..config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        # Support multiple naming conventions for settings
        self.smtp_server = getattr(settings, 'smtp_server', 
                                 getattr(settings, 'SMTP_HOST', 
                                       getattr(settings, 'smtp_host', 'smtp.gmail.com')))
        self.smtp_port = getattr(settings, 'smtp_port', 
                               getattr(settings, 'SMTP_PORT', 587))
        self.smtp_username = getattr(settings, 'smtp_username', 
                                   getattr(settings, 'SMTP_USERNAME', ''))
        self.smtp_password = getattr(settings, 'smtp_password', 
                                   getattr(settings, 'SMTP_PASSWORD', ''))
        self.from_email = getattr(settings, 'smtp_from_email', 
                                getattr(settings, 'SMTP_FROM_EMAIL', ''))
        self.from_name = getattr(settings, 'smtp_from_name', 
                               getattr(settings, 'SMTP_FROM_NAME', 'Lunance'))

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP - Using your working configuration"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # Use STARTTLS for port 587 (your working method)
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password,
                timeout=30
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_email_with_retry(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        max_retries: int = 3
    ) -> bool:
        """Send email with retry mechanism - Your working version"""
        for attempt in range(max_retries):
            try:
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = f"{self.from_name} <{self.from_email}>"
                message["To"] = to_email

                if text_content:
                    text_part = MIMEText(text_content, "plain", "utf-8")
                    message.attach(text_part)

                html_part = MIMEText(html_content, "html", "utf-8")
                message.attach(html_part)

                # Try different connection methods (your working version)
                connection_methods = [
                    # Method 1: STARTTLS (port 587) - most common and working
                    {
                        "use_tls": False,
                        "start_tls": True,
                        "port": 587
                    },
                    # Method 2: SSL from start (port 465)
                    {
                        "use_tls": True,
                        "start_tls": False,
                        "port": 465
                    },
                    # Method 3: Use configured port with STARTTLS
                    {
                        "use_tls": False,
                        "start_tls": True,
                        "port": self.smtp_port
                    },
                    # Method 4: Use configured port with SSL
                    {
                        "use_tls": True,
                        "start_tls": False,
                        "port": self.smtp_port
                    }
                ]

                for method in connection_methods:
                    try:
                        await aiosmtplib.send(
                            message,
                            hostname=self.smtp_server,
                            port=method["port"],
                            use_tls=method["use_tls"],
                            start_tls=method["start_tls"],
                            username=self.smtp_username,
                            password=self.smtp_password,
                            timeout=30
                        )
                        
                        logger.info(f"Email sent successfully to {to_email} using port {method['port']}")
                        return True
                        
                    except Exception as method_error:
                        logger.warning(f"Connection method failed (port {method['port']}): {str(method_error)}")
                        continue

                # If all methods failed for this attempt
                logger.warning(f"Attempt {attempt + 1} failed for {to_email}")
                
                # Wait before retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {to_email}: {str(e)}")

        logger.error(f"All {max_retries} attempts failed for {to_email}")
        return False

    async def send_otp_email(self, to_email: str, otp_code: str, otp_type: str = "registration") -> bool:
        """Send OTP verification email - Updated for Lunance"""
        otp_type_labels = {
            "registration": "Pendaftaran Akun",
            "register": "Pendaftaran Akun",
            "forgot_password": "Reset Password",
            "reset_password": "Reset Password",
            "email_verification": "Verifikasi Email",
            "login_verification": "Verifikasi Login",
            "login_2fa": "Verifikasi Login"
        }
        
        type_label = otp_type_labels.get(otp_type, "Verifikasi")
        subject = f"Kode Verifikasi {type_label} - Lunance"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kode Verifikasi OTP</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .otp-code {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    border-radius: 15px;
                    padding: 25px;
                    margin: 30px 0;
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                    box-shadow: 0 5px 20px rgba(240, 147, 251, 0.3);
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 25px 0;
                    color: #856404;
                    border-left: 5px solid #ffc107;
                }}
                .info-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 25px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 25px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .emoji {{
                    font-size: 24px;
                    margin-right: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🌙 Lunance</div>
                    <h2>Kode Verifikasi {type_label}</h2>
                    <p>Smart Personal Finance Management</p>
                </div>
                <div class="content">
                    <h2>Hai!</h2>
                    <p>Berikut adalah kode verifikasi untuk {type_label.lower()} Anda di Lunance:</p>
                    
                    <div class="otp-code">
                        {otp_code}
                    </div>
                    
                    <div class="info-box">
                        <span class="emoji">⏰</span>
                        <strong>Kode ini akan kadaluarsa dalam 5 menit</strong>
                    </div>
                    
                    <p>Masukkan kode ini di aplikasi Lunance untuk melanjutkan proses {type_label.lower()}.</p>
                    
                    <div class="warning">
                        <span class="emoji">⚠️</span>
                        <strong>Peringatan Keamanan:</strong><br>
                        Jangan bagikan kode ini kepada siapa pun. Tim Lunance tidak akan pernah meminta kode verifikasi Anda melalui telepon atau email.
                    </div>
                    
                    <p>Jika Anda tidak meminta kode ini, abaikan email ini dan pastikan akun Anda aman.</p>
                </div>
                <div class="footer">
                    <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
                    <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                    <p>Butuh bantuan? Hubungi support@lunance.app</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Lunance - Kode Verifikasi {type_label}
        
        Hai!
        
        Berikut adalah kode verifikasi untuk {type_label.lower()} Anda di Lunance:
        
        {otp_code}
        
        Kode ini akan kadaluarsa dalam 5 menit.
        
        Masukkan kode ini di aplikasi Lunance untuk melanjutkan.
        
        PERINGATAN: Jangan bagikan kode ini kepada siapa pun.
        
        Jika Anda tidak meminta kode ini, abaikan email ini.
        
        © 2024 Lunance App
        Smart Personal Finance Management
        """
        
        # Use retry mechanism for important emails like OTP
        return await self.send_email_with_retry(to_email, subject, html_content, text_content)

    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email after successful registration"""
        subject = "Selamat Datang di Lunance! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Selamat Datang!</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .feature {{
                    display: flex;
                    align-items: center;
                    margin: 25px 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #f093fb 10%, #f5576c 100%);
                    border-radius: 12px;
                    color: white;
                }}
                .feature-icon {{
                    font-size: 32px;
                    margin-right: 20px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 18px 35px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 25px 0;
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 25px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌙 Selamat Datang, {user_name}!</h1>
                    <p>Akun Lunance Anda telah berhasil dibuat</p>
                </div>
                <div class="content">
                    <h2>Mulai Kelola Keuangan Pintar Anda!</h2>
                    <p>Terima kasih telah bergabung dengan Lunance. Kami siap membantu Anda mengelola keuangan dengan lebih cerdas dan efisien.</p>
                    
                    <h3>Fitur-fitur canggih yang bisa Anda gunakan:</h3>
                    
                    <div class="feature">
                        <span class="feature-icon">💰</span>
                        <div>
                            <strong>Pelacakan Pengeluaran Otomatis</strong><br>
                            Monitor setiap transaksi dengan kategorisasi pintar
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">🎯</span>
                        <div>
                            <strong>Target Menabung Cerdas</strong><br>
                            AI membantu merencanakan dan mencapai tujuan finansial
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">📊</span>
                        <div>
                            <strong>Analisis & Prediksi</strong><br>
                            Insight mendalam dan prediksi pengeluaran masa depan
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">🏫</span>
                        <div>
                            <strong>Integrasi Universitas</strong><br>
                            Fitur khusus untuk mahasiswa dan kehidupan kampus
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="#" class="cta-button">🚀 Mulai Eksplorasi Sekarang</a>
                    </div>
                    
                    <p>Jika Anda butuh bantuan atau memiliki pertanyaan, tim support kami siap membantu 24/7.</p>
                </div>
                <div class="footer">
                    <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
                    <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                    <p>Butuh bantuan? Hubungi support@lunance.app</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)

    def get_config_status(self) -> dict:
        """Get email service configuration status"""
        return {
            "configured": bool(self.smtp_server and self.smtp_username and self.smtp_password),
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "username": self.smtp_username,
            "from_email": self.from_email,
            "from_name": self.from_name,
            "password_set": bool(self.smtp_password)
        }


# Global email service instance
email_service = EmailService()