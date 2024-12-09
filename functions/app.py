from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from email_validator import validate_email, EmailNotValidError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('SMTP_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('SMTP_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('SMTP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('NOTIFICATION_EMAIL')

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    selected_package = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, contacted, completed

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'selected_package': self.selected_package,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'status': self.status
        }

# Admin views
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class ContactModelView(SecureModelView):
    column_list = ('name', 'email', 'phone', 'selected_package', 'status', 'created_at')
    column_searchable_list = ['name', 'email', 'phone']
    column_filters = ['status', 'selected_package', 'created_at']
    can_export = True
    can_view_details = True
    can_edit = True

# Initialize Admin
admin = Admin(app, name='CareerCraft Pro Admin', template_mode='bootstrap3')
admin.add_view(ContactModelView(Contact, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    # Create admin user if it doesn't exist
    if not User.query.filter_by(username=os.getenv('ADMIN_USERNAME')).first():
        admin_user = User(username=os.getenv('ADMIN_USERNAME'), is_admin=True)
        admin_user.set_password(os.getenv('ADMIN_PASSWORD'))
        db.session.add(admin_user)
        db.session.commit()

def send_notification_email(contact):
    """Send email notification for new contact submission"""
    try:
        msg = Message(
            'New Contact Form Submission',
            recipients=[os.getenv('NOTIFICATION_EMAIL')],
            body=f'''
New contact form submission received:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}
Package: {contact.selected_package}
Message: {contact.message}

Submitted at: {contact.created_at}

Access the admin panel to manage this submission.
'''
        )
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per minute")
def submit_contact():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'email', 'selected_package']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'error': f'Missing required field: {field}'
            }), 400
    
    # Validate email
    try:
        validate_email(data['email'])
    except EmailNotValidError:
        return jsonify({
            'error': 'Invalid email address'
        }), 400
    
    # Create new contact
    contact = Contact(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        selected_package=data['selected_package'],
        message=data.get('message', '')
    )
    
    try:
        db.session.add(contact)
        db.session.commit()
        
        # Send email notification
        send_notification_email(contact)
        
        return jsonify({
            'message': 'Contact form submitted successfully',
            'contact': contact.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save contact information'
        }), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/contacts', methods=['GET'])
@token_required
def get_contacts(current_user):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
        return jsonify({
            'contacts': [contact.to_dict() for contact in contacts]
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve contacts'
        }), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            return redirect(url_for('admin.index'))
        return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
