import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_form_submission():
    # Form data simulation
    form_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'package': 'Professional Resume Package',
        'message': 'This is a test submission.'
    }
    
    try:
        # Email settings
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'xiuxiu.luo@gmail.com'
        smtp_password = 'zlgkpoioieiqaips'
        notification_email = 'xiuxiu.luo@gmail.com'

        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = notification_email
        msg['Subject'] = 'New Resume Request - Test Submission'

        # Email body
        body = f'''
New resume request received:

Name: {form_data['name']}
Email: {form_data['email']}
Phone: {form_data['phone']}
Package: {form_data['package']}
Message: {form_data['message']}

This is a test submission.
'''
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server and send email
        print("\n1. Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("2. Starting TLS...")
            server.starttls()
            
            print("3. Logging in...")
            server.login(smtp_username, smtp_password)
            
            print("4. Sending email...")
            server.send_message(msg)
            
            print("\n✅ Success! Form submission test completed.")
            print("- Email notification sent")
            print("- Check your inbox for the test email")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your Gmail App Password")
        print("2. Verify 2-Step Verification is enabled")
        print("3. Check for any security alerts in Gmail")

if __name__ == '__main__':
    test_form_submission()
