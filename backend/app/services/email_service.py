import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
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

            # Determine SSL/TLS settings based on port
            if self.smtp_port == 465:
                # Port 465 uses implicit SSL (SSL from the start)
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=True,  # Use SSL from connection start
                    username=self.smtp_username,
                    password=self.smtp_password,
                )
            elif self.smtp_port == 587:
                # Port 587 uses explicit TLS (STARTTLS)
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    start_tls=True,  # Use STARTTLS
                    username=self.smtp_username,
                    password=self.smtp_password,
                )
            else:
                # For other ports, try without encryption first
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
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
        """Send email with retry mechanism"""
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

                # Try different connection methods
                connection_methods = [
                    # Method 1: SSL from start (port 465)
                    {
                        "use_tls": True,
                        "start_tls": False,
                        "port": 465
                    },
                    # Method 2: STARTTLS (port 587)
                    {
                        "use_tls": False,
                        "start_tls": True,
                        "port": 587
                    },
                    # Method 3: Use configured port with SSL
                    {
                        "use_tls": True,
                        "start_tls": False,
                        "port": self.smtp_port
                    },
                    # Method 4: Use configured port with STARTTLS
                    {
                        "use_tls": False,
                        "start_tls": True,
                        "port": self.smtp_port
                    }
                ]

                for method in connection_methods:
                    try:
                        await aiosmtplib.send(
                            message,
                            hostname=self.smtp_host,
                            port=method["port"],
                            use_tls=method["use_tls"],
                            start_tls=method["start_tls"],
                            username=self.smtp_username,
                            password=self.smtp_password,
                            timeout=30  # Add timeout
                        )
                        
                        logger.info(f"Email sent successfully to {to_email} using port {method['port']}")
                        return True
                        
                    except Exception as method_error:
                        logger.warning(f"Connection method failed (port {method['port']}): {str(method_error)}")
                        continue

                # If all methods failed for this attempt
                logger.warning(f"Attempt {attempt + 1} failed for {to_email}")
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {to_email}: {str(e)}")

        logger.error(f"All {max_retries} attempts failed for {to_email}")
        return False

    async def send_otp_email(self, to_email: str, otp_code: str, otp_type: str) -> bool:
        """Send OTP verification email"""
        otp_type_labels = {
            "registration": "Pendaftaran Akun",
            "forgot_password": "Reset Password",
            "email_verification": "Verifikasi Email",
            "login_verification": "Verifikasi Login"
        }
        
        type_label = otp_type_labels.get(otp_type, "Verifikasi")
        subject = f"Kode Verifikasi {type_label} - Student Finance"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
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
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .otp-code {{
                    background-color: #f8f9fa;
                    border: 2px dashed #667eea;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 5px;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Student Finance</h1>
                    <p>Kode Verifikasi {type_label}</p>
                </div>
                <div class="content">
                    <h2>Hai!</h2>
                    <p>Berikut adalah kode verifikasi untuk {type_label.lower()} Anda:</p>
                    
                    <div class="otp-code">
                        {otp_code}
                    </div>
                    
                    <p>Kode ini akan kadaluarsa dalam <strong>10 menit</strong>.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Peringatan Keamanan:</strong><br>
                        Jangan bagikan kode ini kepada siapa pun. Tim Student Finance tidak akan pernah meminta kode verifikasi Anda.
                    </div>
                    
                    <p>Jika Anda tidak meminta kode ini, abaikan email ini.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Student Finance App. Semua hak dilindungi.</p>
                    <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Student Finance - Kode Verifikasi {type_label}
        
        Hai!
        
        Berikut adalah kode verifikasi untuk {type_label.lower()} Anda:
        
        {otp_code}
        
        Kode ini akan kadaluarsa dalam 10 menit.
        
        PERINGATAN: Jangan bagikan kode ini kepada siapa pun.
        
        Jika Anda tidak meminta kode ini, abaikan email ini.
        
        © 2024 Student Finance App
        """
        
        # Use retry mechanism for important emails like OTP
        return await self.send_email_with_retry(to_email, subject, html_content, text_content)

    async def send_welcome_email(self, to_email: str, student_name: str) -> bool:
        """Send welcome email after successful registration"""
        subject = "Selamat Datang di Student Finance! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
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
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                }}
                .feature-icon {{
                    font-size: 24px;
                    margin-right: 15px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Selamat Datang, {student_name}!</h1>
                    <p>Akun Student Finance Anda telah berhasil dibuat</p>
                </div>
                <div class="content">
                    <h2>Mulai Kelola Keuangan Mahasiswa Anda!</h2>
                    <p>Terima kasih telah bergabung dengan Student Finance. Kami siap membantu Anda mengelola keuangan dengan lebih baik sebagai mahasiswa.</p>
                    
                    <h3>Fitur yang bisa Anda gunakan:</h3>
                    
                    <div class="feature">
                        <span class="feature-icon">💰</span>
                        <div>
                            <strong>Pelacakan Pengeluaran</strong><br>
                            Monitor pengeluaran harian dengan kategori khusus mahasiswa
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">🎯</span>
                        <div>
                            <strong>Target Menabung</strong><br>
                            Tetapkan dan capai tujuan finansial Anda
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">👥</span>
                        <div>
                            <strong>Bagi Tagihan</strong><br>
                            Mudah berbagi biaya dengan teman-teman
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">📊</span>
                        <div>
                            <strong>Analisis Cerdas</strong><br>
                            Dapatkan insight dan prediksi pengeluaran
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="#" class="cta-button">Mulai Sekarang</a>
                    </div>
                    
                    <p>Jika Anda butuh bantuan, jangan ragu untuk menghubungi tim support kami.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Student Finance App. Semua hak dilindungi.</p>
                    <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)


# Global email service instance
email_service = EmailService()