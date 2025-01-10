from flask import Flask, redirect, url_for, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, time
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email.utils import formataddr
from email.utils import formatdate
from email.utils import make_msgid
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    consultant = db.relationship('User', backref='time_slots')
    consultation = db.relationship('Consultation', backref='time_slot', uselist=False)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    meeting_link = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contact = db.relationship('Contact', backref='consultations')

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    selected_package = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Custom admin views
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class ContactModelView(SecureModelView):
    column_list = ('created_at', 'name', 'email', 'phone', 'selected_package')
    column_searchable_list = ['name', 'email', 'phone']
    column_filters = ['selected_package', 'created_at']
    column_default_sort = ('created_at', True)  # Sort by created_at in descending order
    can_create = False  # Disable creation from admin
    can_edit = True
    can_delete = True
    can_export = True
    can_view_details = True
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    column_labels = {
        'created_at': 'Submitted At',
        'name': 'Full Name',
        'selected_package': 'Package'
    }

    # Add action buttons
    action_disallowed_list = ['delete']
    
    def _send_email(self, contact, template_name, **kwargs):
        try:
            # Email settings
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_username = 'xiuxiu.luo@gmail.com'
            smtp_password = 'zlgkpoioieiqaips'
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_username
            msg['To'] = contact.email
            msg['Subject'] = kwargs.get('subject', 'ResumeHub - Your Resume Request')

            # Load and render template
            template_path = f'templates/emails/{template_name}.html'
            with open(template_path, 'r') as file:
                template_content = file.read()
                
            # Replace placeholders
            template_data = {
                'name': contact.name,
                'package': contact.selected_package,
                'date': contact.created_at.strftime('%Y-%m-%d %H:%M'),
                **kwargs
            }
            
            for key, value in template_data.items():
                template_content = template_content.replace('{{' + key + '}}', str(value))

            # Attach HTML content
            msg.attach(MIMEText(template_content, 'html'))

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                
            flash(f'Email sent successfully to {contact.email}', 'success')
            
        except Exception as e:
            flash(f'Failed to send email: {str(e)}', 'error')

    @action('send_confirmation', 'Send Confirmation Email')
    def action_send_confirmation(self, ids):
        try:
            for contact_id in ids:
                contact = Contact.query.get(contact_id)
                if contact:
                    self._send_email(contact, 'confirmation')
        except Exception as e:
            flash(f'Failed to send confirmation email: {str(e)}', 'error')

    @action('schedule_consultation', 'Schedule Consultation')
    def action_schedule_consultation(self, ids):
        try:
            for contact_id in ids:
                contact = Contact.query.get(contact_id)
                if contact:
                    # Get available time slots
                    available_slots = TimeSlot.query.filter_by(is_available=True)\
                        .filter(TimeSlot.date >= date.today())\
                        .order_by(TimeSlot.date, TimeSlot.start_time)\
                        .limit(3)\
                        .all()
                    
                    if available_slots:
                        # Use the first available slot
                        slot = available_slots[0]
                        
                        # Create consultation
                        consultation = Consultation(
                            contact_id=contact.id,
                            time_slot_id=slot.id,
                            meeting_link=f"https://zoom.us/j/{random.randint(10000000000, 99999999999)}"
                        )
                        
                        # Mark slot as unavailable
                        slot.is_available = False
                        
                        db.session.add(consultation)
                        db.session.commit()
                        
                        # Send email
                        consultation_data = {
                            'consultation_date': slot.date.strftime('%Y-%m-%d'),
                            'consultation_time': slot.start_time.strftime('%I:%M %p'),
                            'platform': 'Zoom',
                            'confirmation_link': consultation.meeting_link,
                            'consultant_name': slot.consultant.username
                        }
                        self._send_email(
                            contact, 
                            'consultation',
                            subject='ResumeHub - Consultation Scheduling',
                            **consultation_data
                        )
                        
                        flash(f'Consultation scheduled for {contact.name}', 'success')
                    else:
                        flash(f'No available time slots for {contact.name}', 'warning')
                        
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to schedule consultation: {str(e)}', 'error')

class TimeSlotView(SecureModelView):
    column_list = ('date', 'start_time', 'end_time', 'is_available', 'consultant', 'created_at')
    column_searchable_list = ['date']
    column_filters = ['date', 'is_available', 'consultant']
    form_columns = ('date', 'start_time', 'end_time', 'consultant')
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.is_available = True
    
    @action('generate_slots', 'Generate Weekly Slots')
    def action_generate_slots(self, ids):
        try:
            # Get the next 2 weeks
            start_date = date.today()
            end_date = start_date + timedelta(days=14)
            current_date = start_date
            
            # Default time slots
            time_slots = [
                (time(9, 0), time(9, 30)),
                (time(10, 0), time(10, 30)),
                (time(11, 0), time(11, 30)),
                (time(14, 0), time(14, 30)),
                (time(15, 0), time(15, 30)),
                (time(16, 0), time(16, 30))
            ]
            
            # Get all consultants (admin users)
            consultants = User.query.filter_by(is_admin=True).all()
            
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    for consultant in consultants:
                        for start, end in time_slots:
                            # Check if slot already exists
                            existing = TimeSlot.query.filter_by(
                                date=current_date,
                                start_time=start,
                                end_time=end,
                                consultant_id=consultant.id
                            ).first()
                            
                            if not existing:
                                slot = TimeSlot(
                                    date=current_date,
                                    start_time=start,
                                    end_time=end,
                                    consultant_id=consultant.id
                                )
                                db.session.add(slot)
                
                current_date += timedelta(days=1)
            
            db.session.commit()
            flash('Successfully generated time slots for the next 2 weeks', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to generate time slots: {str(e)}', 'error')

class ConsultationView(SecureModelView):
    column_list = ('contact', 'time_slot', 'status', 'meeting_link', 'created_at')
    column_searchable_list = ['status']
    column_filters = ['status', 'created_at']
    form_columns = ('contact', 'time_slot', 'status', 'meeting_link', 'notes')
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            # Mark the time slot as unavailable
            model.time_slot.is_available = False
            
            # Generate Zoom meeting link (you can integrate with Zoom API here)
            model.meeting_link = f"https://zoom.us/j/{random.randint(10000000000, 99999999999)}"
            
            # Send confirmation email
            self.send_consultation_confirmation(model)
    
    def send_consultation_confirmation(self, consultation):
        try:
            contact = consultation.contact
            time_slot = consultation.time_slot
            
            consultation_data = {
                'consultation_date': time_slot.date.strftime('%Y-%m-%d'),
                'consultation_time': time_slot.start_time.strftime('%I:%M %p'),
                'platform': 'Zoom',
                'confirmation_link': consultation.meeting_link,
                'consultant_name': time_slot.consultant.username
            }
            
            # Use the existing email sending function
            contact_view = self.session.query(ContactModelView).first()
            if contact_view:
                contact_view._send_email(
                    contact, 
                    'consultation',
                    subject='ResumeHub - Consultation Confirmed',
                    **consultation_data
                )
        except Exception as e:
            flash(f'Failed to send consultation confirmation: {str(e)}', 'error')

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    @expose('/')
    def index(self):
        contacts_count = Contact.query.count()
        recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(5).all()
        return self.render('admin/index.html', 
                         contacts_count=contacts_count,
                         recent_contacts=recent_contacts)

# Initialize admin
admin = Admin(
    app, 
    name='ResumeHub Admin', 
    template_mode='bootstrap3',
    index_view=CustomAdminIndexView()
)
admin.add_view(ContactModelView(Contact, db.session))
admin.add_view(TimeSlotView(TimeSlot, db.session))
admin.add_view(ConsultationView(Consultation, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Create admin templates directory
os.makedirs('templates/admin', exist_ok=True)

# Create database and admin user
with app.app_context():
    db.create_all()
    # Create admin user if it doesn't exist
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if not User.query.filter_by(username=admin_username).first():
        admin_user = User(username=admin_username, is_admin=True)
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{admin_username}' created successfully!")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
