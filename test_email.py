from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

def send_test_email():
    # Email configuration
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    notification_email = os.getenv('NOTIFICATION_EMAIL')

    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = notification_email
    msg['Subject'] = 'Test Email from ResumeHub'
    body = 'This is a test email to verify your email configuration is working correctly.'
    msg.attach(MIMEText(body, 'plain'))

    try:
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            print("Attempting to login...")
            server.login(smtp_username, smtp_password)
            
            print("Sending email...")
            server.send_message(msg)
            
            print("\n✅ Email sent successfully! Check your inbox.\n")
            
    except Exception as e:
        print(f"\n❌ Error sending email: {str(e)}\n")
        print("Please check:")
        print("1. Your Gmail App Password is correct")
        print("2. 2-Step Verification is enabled")
        print("3. Less secure app access is disabled")

if __name__ == '__main__':
    send_test_email()
