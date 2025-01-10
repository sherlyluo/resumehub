# ResumeHub

A professional resume service platform with consultation scheduling and email notifications.

## Features

- Contact form for resume service requests
- Admin dashboard for managing submissions
- Consultation scheduling system
- Email notifications
- Secure authentication

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resumehub.git
cd resumehub
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
FLASK_SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
NOTIFICATION_EMAIL=your-email@gmail.com
```

4. Initialize the database:
```bash
python setup_db.py
```

5. Run the application:
```bash
python admin_app.py
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set environment variables:
```bash
vercel env add FLASK_SECRET_KEY
vercel env add SMTP_USERNAME
vercel env add SMTP_PASSWORD
vercel env add NOTIFICATION_EMAIL
```

## Development

- The application uses Flask for the backend
- SQLite database for data storage
- Flask-Admin for the admin interface
- Flask-Mail for email notifications

## Security

- All passwords are hashed
- Session-based authentication
- CSRF protection
- Secure cookie settings

## License

MIT License
