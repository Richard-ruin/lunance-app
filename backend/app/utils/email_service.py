import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name

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

            # Use STARTTLS for port 587 (most common)
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
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
                    # Method 1: STARTTLS (port 587) - most common
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
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {to_email}: {str(e)}")

        logger.error(f"All {max_retries} attempts failed for {to_email}")
        return False

    async def send_otp_email(self, to_email: str, otp_code: str, otp_type: str = "registration") -> bool:
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

async def send_university_notification_email(
    user_email: str, 
    user_name: str, 
    university_name: str, 
    faculty: str, 
    study_program: str, 
    status: str, 
    admin_notes: str = ""
) -> bool:
    """Send university request notification email"""
    
    if status == "approved":
        subject = "Permintaan Universitas Disetujui - Student Finance"
        status_color = "#28a745"
        status_icon = "✅"
        status_text = "Disetujui"
        message = "Kabar baik! Permintaan Anda untuk menambahkan universitas telah disetujui oleh admin."
    else:
        subject = "Permintaan Universitas Ditolak - Student Finance"
        status_color = "#dc3545"
        status_icon = "❌"
        status_text = "Ditolak"
        message = "Kami informasikan bahwa permintaan Anda untuk menambahkan universitas telah ditolak oleh admin."
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Permintaan Universitas {status_text}</title>
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
                background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .university-info {{
                background-color: #f8f9fa;
                border-left: 4px solid {status_color};
                padding: 20px;
                margin: 20px 0;
            }}
            .notes-box {{
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
                <h1>{status_icon} Permintaan {status_text}</h1>
                <p>Student Finance</p>
            </div>
            <div class="content">
                <h2>Halo {user_name},</h2>
                
                <p>{message}</p>
                
                <div class="university-info">
                    <h3>Detail Universitas:</h3>
                    <p><strong>Nama Universitas:</strong> {university_name}</p>
                    <p><strong>Fakultas:</strong> {faculty}</p>
                    <p><strong>Program Studi:</strong> {study_program}</p>
                </div>
                
                {f'<div class="notes-box"><strong>💬 Catatan Admin:</strong><br>{admin_notes}</div>' if admin_notes else ''}
                
                {f'<p>Anda sekarang dapat menggunakan universitas ini dalam profil Anda. Silakan login kembali untuk melihat perubahan.</p>' if status == 'approved' else '<p>Anda dapat mengajukan permintaan baru dengan informasi yang lebih lengkap dan akurat.</p>'}
                
                <p>Terima kasih{'!!' if status == 'approved' else ' atas pengertiannya.'}</p>
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
    Student Finance - Permintaan Universitas {status_text}
    
    Halo {user_name},
    
    {message}
    
    Detail Universitas:
    - Nama Universitas: {university_name}
    - Fakultas: {faculty}
    - Program Studi: {study_program}
    
    {f'Catatan Admin: {admin_notes}' if admin_notes else ''}
    
    {f'Anda sekarang dapat menggunakan universitas ini dalam profil Anda.' if status == 'approved' else 'Anda dapat mengajukan permintaan baru dengan informasi yang lebih lengkap.'}
    
    Terima kasih!
    
    © 2024 Student Finance App
    """
    
    return await email_service.send_email_with_retry(
        to_email=user_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )

# Update global email service instance
email_service = EmailService()