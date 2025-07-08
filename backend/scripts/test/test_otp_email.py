# scripts/final_otp_test.py
"""Final OTP test using your working email service implementation."""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import EmailService
from app.utils.otp import generate_secure_otp
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_otp_to_ulbi():
    """Test OTP email to ULBI using working email service."""
    print("🚀 Final OTP Test - Lunance Email Service")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailService()
    config = email_service.get_config_status()
    
    print(f"📧 SMTP Server: {config['smtp_server']}")
    print(f"🔌 SMTP Port: {config['smtp_port']}")
    print(f"👤 Username: {config['username']}")
    print(f"📮 From Email: {config['from_email']}")
    print(f"📝 From Name: {config['from_name']}")
    print(f"✅ Configured: {config['configured']}")
    print()
    
    if not config['configured']:
        print("❌ Email service not configured properly!")
        print("Please check your .env file and ensure these settings are set:")
        print("   - smtp_server (or SMTP_HOST)")
        print("   - smtp_port (or SMTP_PORT)")
        print("   - smtp_username (or SMTP_USERNAME)")
        print("   - smtp_password (or SMTP_PASSWORD)")
        print("   - smtp_from_email (or SMTP_FROM_EMAIL)")
        return False
    
    # Generate OTP
    otp_code = generate_secure_otp()
    print(f"🔢 Generated OTP: {otp_code}")
    
    # Send OTP email
    to_email = "613220025@std.ulbi.ac.id"
    print(f"📤 Sending OTP email to {to_email}...")
    
    try:
        success = await email_service.send_otp_email(
            to_email=to_email,
            otp_code=otp_code,
            otp_type="register"
        )
        
        if success:
            print("✅ OTP email sent successfully!")
            print(f"🔢 Your OTP code: {otp_code}")
            print(f"📬 Check your inbox at: {to_email}")
            print("⏰ OTP expires in 5 minutes")
            print()
            print("🎉 Email service is working perfectly!")
            print("🌙 Welcome to Lunance - Smart Personal Finance Management!")
            return True
        else:
            print("❌ Failed to send OTP email")
            print("🔍 Check logs above for error details")
            return False
            
    except Exception as e:
        print(f"❌ Error sending OTP: {e}")
        logger.error(f"OTP send error: {e}")
        return False


async def test_simple_email():
    """Test simple email sending."""
    print("📧 Simple Email Test")
    print("=" * 30)
    
    email_service = EmailService()
    to_email = "613220025@std.ulbi.ac.id"
    
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                <h1>🌙 Lunance</h1>
                <h2>Simple Email Test</h2>
            </div>
            <div style="padding: 30px;">
                <h2>🧪 Test Email Successful!</h2>
                <p>Congratulations! The Lunance email service is working correctly.</p>
                <p>This email was sent using your working SMTP configuration.</p>
                <hr>
                <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = """
    Lunance - Simple Email Test
    
    Test Email Successful!
    
    Congratulations! The Lunance email service is working correctly.
    This email was sent using your working SMTP configuration.
    
    © 2024 Lunance App - Smart Personal Finance Management
    """
    
    try:
        success = await email_service.send_email(
            to_email=to_email,
            subject="[TEST] Lunance Email Service - Simple Test",
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print("✅ Simple email sent successfully!")
            print(f"📬 Check your inbox at: {to_email}")
            return True
        else:
            print("❌ Simple email failed")
            return False
            
    except Exception as e:
        print(f"❌ Error sending simple email: {e}")
        return False


async def main():
    """Main function with test options."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "otp":
            await test_otp_to_ulbi()
        elif command == "simple":
            await test_simple_email()
        elif command == "both":
            print("🔄 Running both tests...\n")
            simple_ok = await test_simple_email()
            print()
            if simple_ok:
                await test_otp_to_ulbi()
            else:
                print("❌ Simple test failed, skipping OTP test")
        else:
            print("Usage:")
            print("  python scripts/final_otp_test.py otp     - Send OTP test")
            print("  python scripts/final_otp_test.py simple  - Send simple test")
            print("  python scripts/final_otp_test.py both    - Send both tests")
    else:
        # Default: OTP test
        await test_otp_to_ulbi()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)