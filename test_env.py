from dotenv import load_dotenv
import os

# Load environment variables
print("Loading environment variables...")
load_dotenv(verbose=True)

# Print email-related environment variables (safely)
print("\nEnvironment Variables:")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD: {'*' * len(os.getenv('SMTP_PASSWORD', ''))} (length: {len(os.getenv('SMTP_PASSWORD', ''))})")
print(f"NOTIFICATION_EMAIL: {os.getenv('NOTIFICATION_EMAIL')}")
