import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.config.settings import Config

logger = logging.getLogger(__name__)

class EmailService:
    """
    Async Email service for sending OTP and notifications
    Uses aiosmtplib with retry mechanism for better reliability
    """
    
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_username = Config.SMTP_USERNAME
        self.smtp_password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM_EMAIL
        self.from_name = Config.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using async SMTP"""
        if Config.DEBUG:
            # In development, just log the email
            logger.info(f"""
=== EMAIL DEBUG MODE ===
To: {to_email}
Subject: {subject}
Content: {text_content or html_content}
=======================
            """)
            return True
        
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
        if Config.DEBUG:
            # In development, just log the email
            logger.info(f"""
=== EMAIL DEBUG MODE (WITH RETRY) ===
To: {to_email}
Subject: {subject}
Content: {text_content or html_content}
Max Retries: {max_retries}
====================================
            """)
            return True
            
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

    @staticmethod
    async def _send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None, use_retry: bool = True):
        """Static method for backward compatibility"""
        email_service = EmailService()
        if use_retry:
            return await email_service.send_email_with_retry(to_email, subject, html_content, text_content)
        else:
            return await email_service.send_email(to_email, subject, html_content, text_content)
    
    @staticmethod
    async def send_verification_otp(email: str, nama: str, otp_code: str) -> bool:
        """Send verification OTP email"""
        subject = "Kode Verifikasi Registrasi Lunance"
        
        text_content = f"""
Halo {nama},

Terima kasih telah mendaftar di Lunance!

Kode verifikasi Anda adalah: {otp_code}

Kode ini berlaku selama 5 menit. Jangan bagikan kode ini kepada siapa pun.

Jika Anda tidak melakukan registrasi, abaikan email ini.

Salam,
Tim Lunance
        """
        
        html_content = f"""
<html>
<head></head>
<body>
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">Lunance</h1>
            <p style="color: white; margin: 10px 0 0 0;">Manajemen Keuangan Mahasiswa</p>
        </div>
        
        <div style="padding: 30px; background-color: #f8f9fa;">
            <h2 style="color: #333; margin-top: 0;">Halo {nama}!</h2>
            <p style="color: #666; line-height: 1.6;">
                Terima kasih telah mendaftar di Lunance. Untuk melanjutkan proses registrasi, 
                silakan gunakan kode verifikasi berikut:
            </p>
            
            <div style="background-color: white; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                <h1 style="color: #667eea; font-size: 32px; margin: 0; letter-spacing: 8px;">{otp_code}</h1>
            </div>
            
            <p style="color: #666; line-height: 1.6;">
                <strong>Kode ini berlaku selama 5 menit.</strong> Jangan bagikan kode ini kepada siapa pun 
                untuk keamanan akun Anda.
            </p>
            
            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                Jika Anda tidak melakukan registrasi, abaikan email ini.
            </p>
        </div>
        
        <div style="background-color: #333; padding: 20px; text-align: center;">
            <p style="color: #ccc; margin: 0; font-size: 14px;">
                © 2025 Lunance. Aplikasi manajemen keuangan untuk mahasiswa.
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        return await EmailService._send_email(email, subject, html_content, text_content, use_retry=True)
    
    @staticmethod
    async def send_password_reset_otp(email: str, nama: str, otp_code: str) -> bool:
        """Send password reset OTP email"""
        subject = "Kode Reset Password Lunance"
        
        text_content = f"""
Halo {nama},

Anda telah meminta reset password untuk akun Lunance Anda.

Kode reset password: {otp_code}

Kode ini berlaku selama 10 menit. Jangan bagikan kode ini kepada siapa pun.

Jika Anda tidak meminta reset password, abaikan email ini dan pastikan akun Anda aman.

Salam,
Tim Lunance
        """
        
        html_content = f"""
<html>
<head></head>
<body>
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">Lunance</h1>
            <p style="color: white; margin: 10px 0 0 0;">Reset Password</p>
        </div>
        
        <div style="padding: 30px; background-color: #f8f9fa;">
            <h2 style="color: #333; margin-top: 0;">Halo {nama}!</h2>
            <p style="color: #666; line-height: 1.6;">
                Anda telah meminta reset password untuk akun Lunance Anda. 
                Gunakan kode berikut untuk reset password:
            </p>
            
            <div style="background-color: white; border: 2px solid #dc3545; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                <h1 style="color: #dc3545; font-size: 32px; margin: 0; letter-spacing: 8px;">{otp_code}</h1>
            </div>
            
            <p style="color: #666; line-height: 1.6;">
                <strong>Kode ini berlaku selama 10 menit.</strong> Jangan bagikan kode ini kepada siapa pun 
                untuk keamanan akun Anda.
            </p>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin: 20px 0;">
                <p style="color: #856404; margin: 0; font-size: 14px;">
                    <strong>Peringatan:</strong> Jika Anda tidak meminta reset password, 
                    abaikan email ini dan pastikan akun Anda aman.
                </p>
            </div>
        </div>
        
        <div style="background-color: #333; padding: 20px; text-align: center;">
            <p style="color: #ccc; margin: 0; font-size: 14px;">
                © 2025 Lunance. Aplikasi manajemen keuangan untuk mahasiswa.
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        return await EmailService._send_email(email, subject, html_content, text_content, use_retry=True)
    
    @staticmethod
    async def send_account_approved(email: str, nama: str) -> bool:
        """Send account approval notification"""
        subject = "Akun Lunance Anda Telah Disetujui!"
        
        text_content = f"""
Halo {nama},

Selamat! Akun Lunance Anda telah disetujui oleh admin.

Anda sekarang dapat login dan mulai menggunakan fitur-fitur Lunance untuk 
mengelola keuangan Anda.

Login di: {Config.FRONTEND_URL}

Salam,
Tim Lunance
        """
        
        html_content = f"""
<html>
<head></head>
<body>
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">🎉 Selamat!</h1>
            <p style="color: white; margin: 10px 0 0 0;">Akun Anda Telah Disetujui</p>
        </div>
        
        <div style="padding: 30px; background-color: #f8f9fa;">
            <h2 style="color: #333; margin-top: 0;">Halo {nama}!</h2>
            <p style="color: #666; line-height: 1.6;">
                Selamat! Akun Lunance Anda telah disetujui oleh admin. 
                Anda sekarang dapat mulai menggunakan aplikasi untuk mengelola keuangan Anda.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{Config.FRONTEND_URL}" 
                   style="background-color: #28a745; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Login Sekarang
                </a>
            </div>
            
            <p style="color: #666; line-height: 1.6;">
                Fitur yang dapat Anda gunakan:
            </p>
            <ul style="color: #666; line-height: 1.6;">
                <li>Catat pemasukan dan pengeluaran</li>
                <li>Buat dan pantau budget</li>
                <li>Analisis pola keuangan</li>
                <li>Set target tabungan</li>
                <li>Dan masih banyak lagi!</li>
            </ul>
        </div>
        
        <div style="background-color: #333; padding: 20px; text-align: center;">
            <p style="color: #ccc; margin: 0; font-size: 14px;">
                © 2025 Lunance. Aplikasi manajemen keuangan untuk mahasiswa.
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        return await EmailService._send_email(email, subject, html_content, text_content, use_retry=True)
    
    @staticmethod
    async def send_account_rejected(email: str, nama: str, reason: str = "") -> bool:
        """Send account rejection notification"""
        subject = "Informasi Terkait Akun Lunance Anda"
        
        reason_text = f"\n\nAlasan: {reason}" if reason else ""
        
        text_content = f"""
Halo {nama},

Maaf, akun Lunance Anda tidak dapat disetujui saat ini.{reason_text}

Jika Anda merasa ini adalah kesalahan atau ingin mengajukan ulang, 
silakan hubungi tim support kami.

Email support: support@lunance.id

Salam,
Tim Lunance
        """
        
        html_content = f"""
<html>
<head></head>
<body>
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">Lunance</h1>
            <p style="color: white; margin: 10px 0 0 0;">Informasi Akun</p>
        </div>
        
        <div style="padding: 30px; background-color: #f8f9fa;">
            <h2 style="color: #333; margin-top: 0;">Halo {nama}!</h2>
            <p style="color: #666; line-height: 1.6;">
                Maaf, akun Lunance Anda tidak dapat disetujui saat ini.
            </p>
            
            {"<div style='background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; padding: 15px; margin: 20px 0;'><p style='color: #721c24; margin: 0;'><strong>Alasan:</strong> " + reason + "</p></div>" if reason else ""}
            
            <p style="color: #666; line-height: 1.6;">
                Jika Anda merasa ini adalah kesalahan atau ingin mengajukan ulang, 
                silakan hubungi tim support kami.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="mailto:support@lunance.id" 
                   style="background-color: #007bff; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Hubungi Support
                </a>
            </div>
        </div>
        
        <div style="background-color: #333; padding: 20px; text-align: center;">
            <p style="color: #ccc; margin: 0; font-size: 14px;">
                © 2025 Lunance. Aplikasi manajemen keuangan untuk mahasiswa.
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        return await EmailService._send_email(email, subject, html_content, text_content, use_retry=True)