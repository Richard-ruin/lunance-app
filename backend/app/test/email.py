# scripts/test_otp_email.py
"""Script to test OTP email functionality."""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import EmailService
from app.utils.email_templates import get_otp_email_template
from app.utils.otp import generate_secure_otp
from app.config.settings import settings
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_email_connection():
    """Test email service connection."""
    print("🔧 Testing email service connection...")
    
    email_service = EmailService()
    
    # Check configuration
    config = email_service.get_config_status()
    print(f"📋 Email Configuration:")
    print(f"   ✅ Configured: {config['configured']}")
    print(f"   📧 SMTP Host: {config['smtp_host']}")
    print(f"   🔌 SMTP Port: {config['smtp_port']}")
    print(f"   👤 Username: {config['username']}")
    print(f"   📮 From Email: {config['from_email']}")
    print(f"   📝 From Name: {config['from_name']}")
    print(f"   🔑 Password Set: {config['password_set']}")
    
    if not config['configured']:
        print("❌ Email service not properly configured!")
        print("Please check your .env file and ensure all SMTP settings are set:")
        print("   - SMTP_HOST")
        print("   - SMTP_PORT") 
        print("   - SMTP_USERNAME")
        print("   - SMTP_PASSWORD")
        print("   - SMTP_FROM_EMAIL")
        return False
    
    # Test connection
    print("\n🔌 Testing SMTP connection...")
    connection_test = await email_service.test_connection()
    
    if connection_test['success']:
        print("✅ SMTP connection successful!")
        return True
    else:
        print(f"❌ SMTP connection failed: {connection_test['message']}")
        return False


async def send_test_otp(email_address: str):
    """Send test OTP email to specified address."""
    print(f"\n📧 Sending test OTP to: {email_address}")
    
    # Generate test OTP
    otp_code = generate_secure_otp()
    print(f"🔢 Generated OTP: {otp_code}")
    
    # Get email template
    template = get_otp_email_template(
        otp_code=otp_code,
        otp_type="register",
        user_name="Test User",
        expires_minutes=5
    )
    
    # Create email service
    email_service = EmailService()
    
    # Send email with retry
    print("📤 Sending email...")
    start_time = datetime.now()
    
    success = await email_service.send_email_with_retry(
        to_email=email_address,
        subject=template["subject"],
        html_content=template["html_content"],
        text_content=template["text_content"],
        max_retries=3
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    if success:
        print(f"✅ Email sent successfully in {duration:.2f} seconds!")
        print(f"📬 Check your inbox at: {email_address}")
        print(f"🔢 Your test OTP code is: {otp_code}")
        print("⏰ OTP expires in 5 minutes")
    else:
        print(f"❌ Failed to send email after {duration:.2f} seconds")
        return False
    
    return True


async def send_multiple_otp_types(email_address: str):
    """Send different types of OTP emails for testing."""
    print(f"\n📧 Sending multiple OTP types to: {email_address}")
    
    otp_types = [
        ("register", "Registration Test"),
        ("reset_password", "Password Reset Test"), 
        ("email_verification", "Email Verification Test"),
        ("login_2fa", "2FA Login Test")
    ]
    
    email_service = EmailService()
    
    for otp_type, description in otp_types:
        print(f"\n📮 Sending {description}...")
        
        otp_code = generate_secure_otp()
        template = get_otp_email_template(
            otp_code=otp_code,
            otp_type=otp_type,
            user_name="Test User",
            expires_minutes=5
        )
        
        success = await email_service.send_email(
            to_email=email_address,
            subject=f"[TEST] {template['subject']}",
            html_content=template["html_content"],
            text_content=template["text_content"]
        )
        
        if success:
            print(f"   ✅ {description} sent successfully! OTP: {otp_code}")
        else:
            print(f"   ❌ {description} failed to send")
        
        # Wait 2 seconds between emails to avoid rate limiting
        await asyncio.sleep(2)


async def interactive_test():
    """Interactive test mode."""
    print("🧪 Lunance Email Service Interactive Test")
    print("=" * 50)
    
    # Test connection first
    connection_ok = await test_email_connection()
    if not connection_ok:
        return
    
    print("\n📧 Email Test Options:")
    print("1. Send single registration OTP")
    print("2. Send all OTP types")
    print("3. Test with custom email")
    print("4. Quick test to 613220025@std.ulbi.ac.id")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        email = input("Enter email address: ").strip()
        await send_test_otp(email)
    
    elif choice == "2":
        email = input("Enter email address: ").strip()
        await send_multiple_otp_types(email)
    
    elif choice == "3":
        email = input("Enter email address: ").strip()
        otp_type = input("Enter OTP type (register/reset_password/email_verification/login_2fa): ").strip()
        if otp_type not in ["register", "reset_password", "email_verification", "login_2fa"]:
            otp_type = "register"
        
        otp_code = generate_secure_otp()
        template = get_otp_email_template(
            otp_code=otp_code,
            otp_type=otp_type,
            user_name="Test User",
            expires_minutes=5
        )
        
        email_service = EmailService()
        success = await email_service.send_email_with_retry(
            to_email=email,
            subject=f"[TEST] {template['subject']}",
            html_content=template["html_content"],
            text_content=template["text_content"]
        )
        
        if success:
            print(f"✅ Test email sent! OTP: {otp_code}")
        else:
            print("❌ Failed to send test email")
    
    elif choice == "4":
        await send_test_otp("613220025@std.ulbi.ac.id")
    
    else:
        print("❌ Invalid choice")


async def quick_test_ulbi():
    """Quick test to the specified ULBI email."""
    print("🚀 Quick Test - Sending OTP to 613220025@std.ulbi.ac.id")
    print("=" * 60)
    
    # Test connection
    connection_ok = await test_email_connection()
    if not connection_ok:
        print("\n❌ Cannot proceed - email service connection failed")
        return
    
    # Send test OTP
    success = await send_test_otp("613220025@std.ulbi.ac.id")
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📱 Please check your email inbox and spam folder")
    else:
        print("\n❌ Test failed - please check your email configuration")


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "quick":
            await quick_test_ulbi()
        elif command == "test" and len(sys.argv) > 2:
            email = sys.argv[2]
            await send_test_otp(email)
        elif command == "connection":
            await test_email_connection()
        else:
            print("Usage:")
            print("  python scripts/test_otp_email.py                    - Interactive mode")
            print("  python scripts/test_otp_email.py quick              - Quick test to ULBI email") 
            print("  python scripts/test_otp_email.py test <email>       - Test specific email")
            print("  python scripts/test_otp_email.py connection         - Test connection only")
    else:
        await interactive_test()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test script error: {e}", exc_info=True)