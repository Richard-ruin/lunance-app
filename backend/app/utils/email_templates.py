# app/utils/email_templates.py
"""Template email dalam bahasa Indonesia untuk berbagai keperluan aplikasi Lunance."""

from typing import Dict, Optional
from datetime import datetime


def get_otp_email_template(
    otp_code: str,
    otp_type: str = "register",
    user_name: str = "Pengguna",
    expires_minutes: int = 5
) -> Dict[str, str]:
    """
    Template email untuk OTP verification.
    
    Args:
        otp_code: Kode OTP
        otp_type: Tipe OTP (register, reset_password, email_verification)
        user_name: Nama pengguna
        expires_minutes: Waktu kadaluarsa dalam menit
        
    Returns:
        Dict dengan subject, html_content, dan text_content
    """
    
    type_labels = {
        "register": "Pendaftaran Akun",
        "reset_password": "Reset Password", 
        "email_verification": "Verifikasi Email",
        "login_verification": "Verifikasi Login"
    }
    
    type_label = type_labels.get(otp_type, "Verifikasi")
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
                <h2>Hai, {user_name}!</h2>
                <p>Berikut adalah kode verifikasi untuk {type_label.lower()} Anda di Lunance:</p>
                
                <div class="otp-code">
                    {otp_code}
                </div>
                
                <div class="info-box">
                    <span class="emoji">⏰</span>
                    <strong>Kode ini akan kadaluarsa dalam {expires_minutes} menit</strong>
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
    
    Hai, {user_name}!
    
    Berikut adalah kode verifikasi untuk {type_label.lower()} Anda di Lunance:
    
    {otp_code}
    
    Kode ini akan kadaluarsa dalam {expires_minutes} menit.
    
    Masukkan kode ini di aplikasi Lunance untuk melanjutkan.
    
    PERINGATAN: Jangan bagikan kode ini kepada siapa pun.
    
    Jika Anda tidak meminta kode ini, abaikan email ini.
    
    © 2024 Lunance App
    Smart Personal Finance Management
    """
    
    return {
        "subject": subject,
        "html_content": html_content,
        "text_content": text_content
    }


def get_notification_email_template(
    user_name: str,
    notification_title: str,
    notification_message: str,
    action_url: Optional[str] = None,
    action_text: Optional[str] = None
) -> Dict[str, str]:
    """
    Template email untuk notifikasi umum.
    
    Args:
        user_name: Nama pengguna
        notification_title: Judul notifikasi
        notification_message: Pesan notifikasi
        action_url: URL action (opsional)
        action_text: Teks button action (opsional)
        
    Returns:
        Dict dengan subject, html_content, dan text_content
    """
    
    subject = f"Lunance - {notification_title}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{notification_title}</title>
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
                padding: 30px;
                text-align: center;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .content {{
                padding: 30px;
            }}
            .notification-box {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }}
            .notification-title {{
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }}
            .notification-message {{
                color: #555;
                line-height: 1.6;
            }}
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 25px;
                text-decoration: none;
                border-radius: 8px;
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
                <div class="logo">🌙 Lunance</div>
                <p>Smart Personal Finance Management</p>
            </div>
            <div class="content">
                <h2>Hai, {user_name}!</h2>
                <p>Anda memiliki notifikasi baru dari Lunance:</p>
                
                <div class="notification-box">
                    <div class="notification-title">{notification_title}</div>
                    <div class="notification-message">{notification_message.replace('\n', '<br>')}</div>
                </div>
                
                {f'''
                <div style="text-align: center;">
                    <a href="{action_url}" class="action-button">
                        {action_text}
                    </a>
                </div>
                ''' if action_url else ''}
                
                <p>Terima kasih telah menggunakan Lunance untuk mengelola keuangan Anda!</p>
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
    Lunance - {notification_title}
    
    Hai, {user_name}!
    
    Anda memiliki notifikasi baru dari Lunance:
    
    {notification_title}
    {notification_message}
    
    {f"Link: {action_url}" if action_url else ""}
    
    Terima kasih telah menggunakan Lunance!
    
    ---
    © 2024 Lunance App
    Smart Personal Finance Management
    """
    
    return {
        "subject": subject,
        "html_content": html_content,
        "text_content": text_content
    }


def get_welcome_email_template(user_name: str) -> Dict[str, str]:
    """
    Template email selamat datang untuk user baru.
    
    Args:
        user_name: Nama pengguna
        
    Returns:
        Dict dengan subject, html_content, dan text_content
    """
    
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
    
    text_content = f"""
    Selamat Datang di Lunance, {user_name}!
    
    Akun Lunance Anda telah berhasil dibuat.
    
    Mulai Kelola Keuangan Pintar Anda!
    
    Terima kasih telah bergabung dengan Lunance. Kami siap membantu Anda mengelola keuangan dengan lebih cerdas dan efisien.
    
    Fitur-fitur canggih yang bisa Anda gunakan:
    
    💰 Pelacakan Pengeluaran Otomatis
    Monitor setiap transaksi dengan kategorisasi pintar
    
    🎯 Target Menabung Cerdas
    AI membantu merencanakan dan mencapai tujuan finansial
    
    📊 Analisis & Prediksi
    Insight mendalam dan prediksi pengeluaran masa depan
    
    🏫 Integrasi Universitas
    Fitur khusus untuk mahasiswa dan kehidupan kampus
    
    Jika Anda butuh bantuan atau memiliki pertanyaan, tim support kami siap membantu 24/7.
    
    © 2024 Lunance App
    Smart Personal Finance Management
    """
    
    return {
        "subject": subject,
        "html_content": html_content,
        "text_content": text_content
    }


def get_password_reset_email_template(
    user_name: str,
    reset_url: str,
    expires_hours: int = 1
) -> Dict[str, str]:
    """
    Template email untuk reset password.
    
    Args:
        user_name: Nama pengguna
        reset_url: URL untuk reset password
        expires_hours: Waktu kadaluarsa dalam jam
        
    Returns:
        Dict dengan subject, html_content, dan text_content
    """
    
    subject = "Reset Password Akun Lunance"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
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
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .reset-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
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
                <h1>🔐 Reset Password</h1>
                <p>Lunance - Smart Personal Finance Management</p>
            </div>
            <div class="content">
                <h2>Hai, {user_name}!</h2>
                <p>Kami menerima permintaan untuk mereset password akun Lunance Anda.</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="reset-button">
                        Reset Password Sekarang
                    </a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Penting:</strong><br>
                    • Link ini akan kadaluarsa dalam {expires_hours} jam<br>
                    • Jika Anda tidak meminta reset password, abaikan email ini<br>
                    • Password Anda akan tetap aman sampai Anda menggunakan link ini
                </div>
                
                <p>Jika tombol di atas tidak berfungsi, copy dan paste link berikut ke browser Anda:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                
                <p>Butuh bantuan? Hubungi tim support kami di support@lunance.app</p>
            </div>
            <div class="footer">
                <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
                <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Reset Password Akun Lunance
    
    Hai, {user_name}!
    
    Kami menerima permintaan untuk mereset password akun Lunance Anda.
    
    Klik link berikut untuk reset password:
    {reset_url}
    
    PENTING:
    • Link ini akan kadaluarsa dalam {expires_hours} jam
    • Jika Anda tidak meminta reset password, abaikan email ini
    • Password Anda akan tetap aman sampai Anda menggunakan link ini
    
    Butuh bantuan? Hubungi tim support kami di support@lunance.app
    
    © 2024 Lunance App
    Smart Personal Finance Management
    """
    
    return {
        "subject": subject,
        "html_content": html_content,
        "text_content": text_content
    }


def get_maintenance_email_template(
    user_name: str,
    start_time: str,
    end_time: str,
    duration: str,
    description: str = "Pemeliharaan rutin sistem"
) -> Dict[str, str]:
    """
    Template email untuk notifikasi maintenance.
    
    Args:
        user_name: Nama pengguna
        start_time: Waktu mulai maintenance
        end_time: Waktu selesai maintenance
        duration: Durasi maintenance
        description: Deskripsi maintenance
        
    Returns:
        Dict dengan subject, html_content, dan text_content
    """
    
    subject = "Pemberitahuan Pemeliharaan Sistem - Lunance"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pemberitahuan Maintenance</title>
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
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .maintenance-info {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                color: #856404;
            }}
            .schedule {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
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
                <h1>🔧 Pemberitahuan Pemeliharaan Sistem</h1>
                <p>Lunance - Smart Personal Finance Management</p>
            </div>
            <div class="content">
                <h2>Hai, {user_name}!</h2>
                <p>Kami ingin memberitahukan bahwa sistem Lunance akan menjalani pemeliharaan terjadwal.</p>
                
                <div class="maintenance-info">
                    <h3>📋 Detail Pemeliharaan:</h3>
                    <p><strong>Jenis:</strong> {description}</p>
                    
                    <div class="schedule">
                        <p><strong>🕐 Mulai:</strong> {start_time} WIB</p>
                        <p><strong>🕐 Selesai:</strong> {end_time} WIB</p>
                        <p><strong>⏱️ Durasi:</strong> {duration}</p>
                    </div>
                </div>
                
                <h3>❓ Apa yang akan terjadi?</h3>
                <ul>
                    <li>Aplikasi mungkin tidak dapat diakses sementara</li>
                    <li>Fitur tertentu mungkin mengalami gangguan</li>
                    <li>Data Anda tetap aman dan tidak akan hilang</li>
                </ul>
                
                <h3>💡 Yang bisa Anda lakukan:</h3>
                <ul>
                    <li>Simpan pekerjaan Anda sebelum waktu maintenance</li>
                    <li>Rencanakan aktivitas lain selama periode ini</li>
                    <li>Coba akses kembali setelah maintenance selesai</li>
                </ul>
                
                <p>Kami mohon maaf atas ketidaknyamanan ini. Pemeliharaan ini dilakukan untuk meningkatkan performa dan keamanan sistem.</p>
                
                <p>Terima kasih atas pengertian Anda!</p>
            </div>
            <div class="footer">
                <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
                <p>Butuh bantuan? Hubungi support@lunance.app</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Pemberitahuan Pemeliharaan Sistem - Lunance
    
    Hai, {user_name}!
    
    Kami ingin memberitahukan bahwa sistem Lunance akan menjalani pemeliharaan terjadwal.
    
    Detail Pemeliharaan:
    Jenis: {description}
    Mulai: {start_time} WIB
    Selesai: {end_time} WIB
    Durasi: {duration}
    
    Apa yang akan terjadi?
    • Aplikasi mungkin tidak dapat diakses sementara
    • Fitur tertentu mungkin mengalami gangguan
    • Data Anda tetap aman dan tidak akan hilang
    
    Yang bisa Anda lakukan:
    • Simpan pekerjaan Anda sebelum waktu maintenance
    • Rencanakan aktivitas lain selama periode ini
    • Coba akses kembali setelah maintenance selesai
    
    Kami mohon maaf atas ketidaknyamanan ini. Pemeliharaan ini dilakukan untuk meningkatkan performa dan keamanan sistem.
    
    Terima kasih atas pengertian Anda!
    
    © 2024 Lunance App
    Smart Personal Finance Management
    """
    
    return {
        "subject": subject,
        "html_content": html_content,
        "text_content": text_content
    }