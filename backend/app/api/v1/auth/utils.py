import smtplib
import aiosmtplib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

from app.config.settings import settings
from app.core.security import (
    create_access_token, create_refresh_token, verify_token,
    generate_otp, generate_secure_token
)
from app.core.exceptions import (
    EmailServiceException, InvalidTokenException, TokenExpiredException
)
from app.models.student import Student, OTPType

logger = logging.getLogger(__name__)


class AuthUtils:
    """Authentication utilities"""
    
    @staticmethod
    def create_tokens_for_student(student: Student) -> Dict[str, str]:
        """Create access and refresh tokens for student"""
        token_data = {
            "sub": student.email,
            "user_id": str(student.id),
            "email": student.email,
            "full_name": student.profile.full_name,
            "university": student.profile.university,
            "verified": student.verification.email_verified
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": student.email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        """Create new access token from refresh token"""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, token_type="refresh")
            email = payload.get("sub")
            
            if not email:
                raise InvalidTokenException()
            
            # Create new tokens (you might want to fetch fresh user data here)
            token_data = {"sub": email}
            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token({"sub": email})
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            raise InvalidTokenException()
    
    @staticmethod
    def extract_user_from_token(token: str) -> Dict[str, Any]:
        """Extract user information from access token"""
        try:
            payload = verify_token(token, token_type="access")
            return {
                "email": payload.get("sub"),
                "user_id": payload.get("user_id"),
                "full_name": payload.get("full_name"),
                "university": payload.get("university"),
                "verified": payload.get("verified", False)
            }
        except Exception as e:
            raise InvalidTokenException()


class EmailService:
    """Email service for sending notifications and OTPs"""
    
    def __init__(self):
        self.smtp_config = settings.smtp_config
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[list] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative" if is_html else "mixed")
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    with open(attachment["path"], "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {attachment['filename']}"
                        )
                        message.attach(part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_config["hostname"],
                port=self.smtp_config["port"],
                start_tls=self.smtp_config["start_tls"],
                username=self.smtp_config["username"],
                password=self.smtp_config["password"],
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise EmailServiceException(f"Failed to send email: {str(e)}")
    
    async def send_otp_email(self, to_email: str, otp_code: str, otp_type: OTPType) -> bool:
        """Send OTP code via email"""
        try:
            # Determine email content based on OTP type
            if otp_type == OTPType.REGISTRATION:
                subject = "Verifikasi Akun Lunance - Kode OTP"
                template = self._get_registration_otp_template(otp_code)
            elif otp_type == OTPType.FORGOT_PASSWORD:
                subject = "Reset Password Lunance - Kode OTP"
                template = self._get_forgot_password_otp_template(otp_code)
            elif otp_type == OTPType.EMAIL_VERIFICATION:
                subject = "Verifikasi Email Lunance - Kode OTP"
                template = self._get_email_verification_otp_template(otp_code)
            else:
                subject = "Lunance - Kode OTP"
                template = self._get_generic_otp_template(otp_code)
            
            return await self.send_email(to_email, subject, template, is_html=True)
            
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            raise EmailServiceException(f"Failed to send OTP email: {str(e)}")
    
    def _get_registration_otp_template(self, otp_code: str) -> str:
        """Get registration OTP email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verifikasi Akun Lunance</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Lunance</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Finance Tracker untuk Mahasiswa</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Selamat Datang di Lunance! 🎉</h2>
                
                <p>Terima kasih telah mendaftar di Lunance. Untuk menyelesaikan pendaftaran akun Anda, silakan gunakan kode OTP berikut:</p>
                
                <div style="background: #f8f9fa; border: 2px dashed #667eea; padding: 20px; margin: 30px 0; text-align: center; border-radius: 8px;">
                    <h3 style="margin: 0; color: #667eea; font-size: 32px; letter-spacing: 5px; font-family: 'Courier New', monospace;">{otp_code}</h3>
                </div>
                
                <p><strong>Penting:</strong></p>
                <ul>
                    <li>Kode OTP ini berlaku selama <strong>{settings.OTP_EXPIRE_MINUTES} menit</strong></li>
                    <li>Jangan bagikan kode ini kepada siapapun</li>
                    <li>Gunakan kode ini hanya di aplikasi Lunance</li>
                </ul>
                
                <p>Jika Anda tidak merasa mendaftar di Lunance, abaikan email ini.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Email ini dikirim secara otomatis. Mohon tidak membalas email ini.<br>
                    <strong>Tim Lunance</strong><br>
                    Platform Finansial untuk Mahasiswa Indonesia
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_forgot_password_otp_template(self, otp_code: str) -> str:
        """Get forgot password OTP email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Password Lunance</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Lunance</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Reset Password</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Reset Password Akun Anda 🔒</h2>
                
                <p>Kami menerima permintaan untuk reset password akun Lunance Anda. Gunakan kode OTP berikut untuk membuat password baru:</p>
                
                <div style="background: #fff5f5; border: 2px dashed #ff6b6b; padding: 20px; margin: 30px 0; text-align: center; border-radius: 8px;">
                    <h3 style="margin: 0; color: #ff6b6b; font-size: 32px; letter-spacing: 5px; font-family: 'Courier New', monospace;">{otp_code}</h3>
                </div>
                
                <p><strong>Perhatian:</strong></p>
                <ul>
                    <li>Kode OTP ini berlaku selama <strong>{settings.OTP_EXPIRE_MINUTES} menit</strong></li>
                    <li>Setelah verifikasi, Anda dapat membuat password baru</li>
                    <li>Jangan bagikan kode ini kepada siapapun</li>
                </ul>
                
                <p>Jika Anda tidak meminta reset password, abaikan email ini dan password Anda akan tetap aman.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Email ini dikirim secara otomatis. Mohon tidak membalas email ini.<br>
                    <strong>Tim Lunance</strong><br>
                    Platform Finansial untuk Mahasiswa Indonesia
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_email_verification_otp_template(self, otp_code: str) -> str:
        """Get email verification OTP template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verifikasi Email Lunance</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Lunance</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Verifikasi Email</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Verifikasi Email Anda ✉️</h2>
                
                <p>Untuk melengkapi verifikasi akun Lunance Anda, silakan gunakan kode OTP berikut:</p>
                
                <div style="background: #f0fffe; border: 2px dashed #4ecdc4; padding: 20px; margin: 30px 0; text-align: center; border-radius: 8px;">
                    <h3 style="margin: 0; color: #4ecdc4; font-size: 32px; letter-spacing: 5px; font-family: 'Courier New', monospace;">{otp_code}</h3>
                </div>
                
                <p><strong>Informasi:</strong></p>
                <ul>
                    <li>Kode OTP ini berlaku selama <strong>{settings.OTP_EXPIRE_MINUTES} menit</strong></li>
                    <li>Email yang terverifikasi diperlukan untuk keamanan akun</li>
                    <li>Jangan bagikan kode ini kepada siapapun</li>
                </ul>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Email ini dikirim secara otomatis. Mohon tidak membalas email ini.<br>
                    <strong>Tim Lunance</strong><br>
                    Platform Finansial untuk Mahasiswa Indonesia
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_generic_otp_template(self, otp_code: str) -> str:
        """Get generic OTP email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kode OTP Lunance</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Lunance</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Kode Verifikasi</p>
            </div>
            
            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Kode OTP Anda</h2>
                
                <p>Berikut adalah kode OTP untuk verifikasi akun Lunance Anda:</p>
                
                <div style="background: #f8f9fa; border: 2px dashed #667eea; padding: 20px; margin: 30px 0; text-align: center; border-radius: 8px;">
                    <h3 style="margin: 0; color: #667eea; font-size: 32px; letter-spacing: 5px; font-family: 'Courier New', monospace;">{otp_code}</h3>
                </div>
                
                <p>Kode ini berlaku selama <strong>{settings.OTP_EXPIRE_MINUTES} menit</strong>. Jangan bagikan kode ini kepada siapapun.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Email ini dikirim secara otomatis. Mohon tidak membalas email ini.<br>
                    <strong>Tim Lunance</strong>
                </p>
            </div>
        </body>
        </html>
        """


class OTPService:
    """OTP service for generating and managing OTP codes"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    async def generate_and_send_otp(self, email: str, otp_type: OTPType) -> str:
        """Generate OTP and send via email"""
        try:
            # Generate OTP code
            otp_code = generate_otp(settings.OTP_LENGTH)
            
            # Send OTP via email
            await self.email_service.send_otp_email(email, otp_code, otp_type)
            
            return otp_code
            
        except Exception as e:
            logger.error(f"Failed to generate and send OTP: {str(e)}")
            raise EmailServiceException(f"Failed to send OTP: {str(e)}")
    
    def generate_password_reset_token(self) -> str:
        """Generate secure token for password reset"""
        return generate_secure_token(32)


# Create global service instances
auth_utils = AuthUtils()
email_service = EmailService()
otp_service = OTPService()