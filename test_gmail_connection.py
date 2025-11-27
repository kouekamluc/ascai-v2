#!/usr/bin/env python
"""
Simple script to test Gmail SMTP connection and diagnose authentication issues.
"""
import smtplib
import sys
from email.mime.text import MIMEText

def test_gmail_connection(email, password):
    """Test Gmail SMTP connection with detailed error reporting."""
    print("=" * 60)
    print("Gmail SMTP Connection Test")
    print("=" * 60)
    print(f"\nEmail: {email}")
    print(f"Password length: {len(password)} characters")
    print(f"Password has spaces: {'Yes' if ' ' in password else 'No'}")
    print(f"Password preview: {password[:4]}...{password[-4:]}")
    
    # Check password format
    if len(password) != 16:
        print(f"\n[WARNING] App Password should be 16 characters, got {len(password)}")
    
    if ' ' in password:
        print("\n[WARNING] Password contains spaces! Remove all spaces.")
        print(f"   Current: '{password}'")
        print(f"   Should be: '{password.replace(' ', '')}'")
        password = password.replace(' ', '')
    
    print("\nAttempting to connect to Gmail SMTP...")
    print("Host: smtp.gmail.com")
    print("Port: 587")
    print("TLS: True")
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("\n[OK] Connected to SMTP server")
        
        # Start TLS
        server.starttls()
        print("[OK] TLS started")
        
        # Login
        print("\nAttempting to login...")
        server.login(email, password)
        print("[OK] Login successful!")
        
        # Close connection
        server.quit()
        print("\n" + "=" * 60)
        print("SUCCESS: Gmail SMTP connection works!")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "=" * 60)
        print("AUTHENTICATION FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPossible causes:")
        print("1. App Password is incorrect or expired")
        print("2. 2-Factor Authentication is not enabled")
        print("3. App Password has spaces (should be removed)")
        print("4. Email address is incorrect")
        print("\nSolutions:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Delete old App Password and create a new one")
        print("3. Make sure 2FA is enabled: https://myaccount.google.com/security")
        print("4. Copy the 16-character password WITHOUT spaces")
        print("5. Update .env.example with the new password")
        return False
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("CONNECTION ERROR")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPossible causes:")
        print("1. Network/firewall blocking port 587")
        print("2. Gmail SMTP server is down")
        print("3. Internet connection issue")
        return False

if __name__ == '__main__':
    # Read from .env.example
    import os
    from pathlib import Path
    
    env_file = Path('.env.example')
    if not env_file.exists():
        print("ERROR: .env.example file not found!")
        sys.exit(1)
    
    # Parse .env.example
    email = None
    password = None
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('EMAIL_HOST_USER='):
                email = line.split('=', 1)[1].strip()
            elif line.startswith('EMAIL_HOST_PASSWORD='):
                password = line.split('=', 1)[1].strip()
    
    if not email or not password:
        print("ERROR: Could not find EMAIL_HOST_USER or EMAIL_HOST_PASSWORD in .env.example")
        sys.exit(1)
    
    if email == 'your-email@gmail.com' or password == 'your-app-password':
        print("ERROR: Please update .env.example with your actual Gmail credentials")
        sys.exit(1)
    
    success = test_gmail_connection(email, password)
    sys.exit(0 if success else 1)

