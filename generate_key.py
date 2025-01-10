import secrets
import string

def generate_secure_password(length=12):
    # Define character sets
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "!@#$%^&*"
    # Combine all characters
    all_chars = letters + digits + special_chars
    
    # Generate password ensuring it contains at least one of each type
    password = [
        secrets.choice(letters.lower()),    # at least one lowercase
        secrets.choice(letters.upper()),    # at least one uppercase
        secrets.choice(digits),             # at least one digit
        secrets.choice(special_chars),      # at least one special char
    ]
    
    # Fill the rest of the password
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password characters
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

# Generate Flask secret key
secret_key = secrets.token_hex(32)

# Generate admin credentials
admin_username = "admin_" + secrets.token_hex(4)  # e.g., admin_1a2b3c4d
admin_password = generate_secure_password(16)

print("\nYour Credentials (save these securely):\n")
print(f"FLASK_SECRET_KEY={secret_key}")
print(f"ADMIN_USERNAME={admin_username}")
print(f"ADMIN_PASSWORD={admin_password}\n")
print("Important: Save these credentials securely and never share them!")
