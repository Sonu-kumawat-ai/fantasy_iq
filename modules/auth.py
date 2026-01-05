"""Authentication related functions for Fantasy IQ application"""
import random
import string
from datetime import datetime, timedelta
from flask_mail import Message

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(mail, email, otp, username):
    """Send OTP email to user"""
    try:
        msg = Message(
            subject='Fantasy IQ - Email Verification OTP',
            recipients=[email]
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 50px auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #ff6b6b;
                    margin: 0;
                }}
                .content {{
                    text-align: center;
                }}
                .otp {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #ff6b6b;
                    background-color: #f9f9f9;
                    padding: 15px 30px;
                    border-radius: 8px;
                    display: inline-block;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .message {{
                    color: #333;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Fantasy IQ</h1>
                </div>
                <div class="content">
                    <p class="message">Hello <strong>{username}</strong>,</p>
                    <p class="message">Thank you for registering with Fantasy IQ! Please use the OTP below to verify your email address:</p>
                    <div class="otp">{otp}</div>
                    <p class="message">This OTP will expire in 10 minutes.</p>
                    <p class="message">If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Fantasy IQ. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False
