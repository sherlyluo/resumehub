import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Hard-coded credentials for testing (we'll move these to .env after confirming it works)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "xiuxiu.luo@gmail.com"
SMTP_PASSWORD = "zlgkpoioieiqaips"
NOTIFICATION_EMAIL = "xiuxiu.luo@gmail.com"

def send_test_email():
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = 'Test Email from ResumeHub'
        body = 'This is a test email to verify your email configuration is working correctly.'
        msg.attach(MIMEText(body, 'plain'))

        print(f"1. Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("2. Starting TLS...")
            server.starttls()
            
            print("3. Attempting to login...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            print("4. Sending email...")
            server.send_message(msg)
            
            print("\n✅ Success! Email sent. Please check your inbox.\n")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("Troubleshooting tips:")
        print("1. Verify your Gmail App Password is correct")
        print("2. Ensure 2-Step Verification is enabled in your Google Account")
        print("3. Check if there are any security alerts in your Gmail account")
        print("4. Try generating a new App Password")

if __name__ == '__main__':
    send_test_email()
