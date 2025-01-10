from admin_app import app, db, User
from datetime import datetime

def setup_database():
    with app.app_context():
        # Drop all tables
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating new tables...")
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_username = 'admin_c71a7f39'
        admin_password = '2FcX3Y#5%HR8$FPU'
        
        if not User.query.filter_by(username=admin_username).first():
            admin_user = User(username=admin_username, is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created admin user: {admin_username}")
        
        print("Database setup complete!")

if __name__ == '__main__':
    setup_database()
