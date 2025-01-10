from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    selected_package = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def send_notification_email(contact):
    """Send email notification for new contact submission"""
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
        msg['Subject'] = 'New Resume Request'

        body = f'''
New resume request received:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}
Package: {contact.selected_package}
Message: {contact.message}

Submitted at: {contact.created_at}
'''
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        print("\nSending email notification...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            print("✅ Email notification sent successfully!")
            
    except Exception as e:
        print(f"❌ Failed to send email notification: {str(e)}")

def test_form_submission():
    with app.app_context():
        # Drop existing database
        try:
            os.remove('instance/contacts.db')
            print("Removed old database")
        except:
            pass
            
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Test data
        test_contact = Contact(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            selected_package="Professional Resume Package",
            message="This is a test submission to verify the form functionality."
        )
        
        try:
            # Save to database
            print("\nSaving to database...")
            db.session.add(test_contact)
            db.session.commit()
            print("✅ Contact saved to database successfully!")
            
            # Send email notification
            send_notification_email(test_contact)
            
            # Verify the saved data
            saved_contact = Contact.query.filter_by(email="test@example.com").first()
            print("\nVerifying saved data:")
            print(f"Name: {saved_contact.name}")
            print(f"Email: {saved_contact.email}")
            print(f"Phone: {saved_contact.phone}")
            print(f"Package: {saved_contact.selected_package}")
            print(f"Created at: {saved_contact.created_at}")
            
        except Exception as e:
            print(f"\n❌ Error during form submission test: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    test_form_submission()
