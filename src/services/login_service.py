import uuid
import random
import string
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Form,Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel,EmailStr
import os
import aiosmtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from src.db import create_db,get_db_connection
from src.models.login_models import SignupRequest,LoginRequest,OTPVerification
import sqlite3
import bcrypt
import re

load_dotenv()
# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

create_db()

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "hello"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

# Email configuration
SMTP_USERNAME = os.getenv('SMTP_MAIL_USERNAME')
SMTP_PASSWORD = os.getenv('PASSWORD')
SMTP_HOST = os.getenv('HOST')         
SMTP_PORT = os.getenv('PORT')

# OTP storage with extended validity
otp_store = {}


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def create_jwt_token(data: dict):
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def send_email(recipient: str, subject: str, body: str):
    message = MIMEText(body, "html")
    message["From"] = SMTP_USERNAME
    message["To"] = recipient
    message["Subject"] = subject

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

# def check_email_exists_or_not(email: str):
#     """Check if an email exists in the user_detailed table (for SQLite)."""
#     conn = get_db_connection()
#     if conn is None:
#         raise HTTPException(status_code=500, detail="Database connection failed")
    
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1 FROM user_detailed WHERE email = ?", (email,))
#         if cursor.fetchone():
#             raise HTTPException(status_code=400, detail="Email already registered")
#         return False  # Email does not exist
#     finally:
#         conn.close()


def validate_name(name: str):
    """Validate that the name contains only alphabets and no spaces."""
    if not name.isalpha():
        raise HTTPException(status_code=400, detail="Name must contain only alphabets with no spaces.")
    return name


def validate_password(password: str):
    """Ensure password meets security standards."""
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
    return password

# # Routes
async def signup(request: SignupRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if email exists
    cursor.execute("SELECT email FROM user_detailed WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user_uuid = str(uuid.uuid4())
    hashed_password = pwd_context.hash(request.password)
    
    try:
        cursor.execute("""
            INSERT INTO user_detailed (uuid, Firstname, lastname, email, password, is_verified)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_uuid, request.firstname, request.lastname, request.email, hashed_password, False))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()

    # Generate and store OTP
    otp = generate_otp()
    otp_store[request.email] = {
        "otp": otp,
        "timestamp": datetime.utcnow(),
        "attempts": 0
    }
    
    # Send OTP email
    try:
        await send_email(
            request.email,
            "Verify your email",
            f"Your verification code is: {otp}. Valid for 5 minutes."
        )
    except Exception as e:
        # return 
        raise HTTPException(status_code=500, detail="Error sending verification email")


    return JSONResponse(
        status_code=200,
        content={
            "message": "Signup successful. Please check your email for verification code.",
            "email": request.email
        }
    )


async def verify_otp(verification: OTPVerification):
    # Check if OTP exists and is valid
    otp_data = otp_store.get(verification.email)
    if not otp_data:
        raise HTTPException(status_code=400, detail="No OTP found for this email")

    # Check OTP expiration (5 minutes)
    time_diff = (datetime.utcnow() - otp_data["timestamp"]).total_seconds()
    if time_diff > 300:  # 5 minutes in seconds
        del otp_store[verification.email]
        raise HTTPException(status_code=400, detail="OTP has expired")

    # Verify OTP
    if verification.otp != otp_data["otp"]:
        otp_data["attempts"] += 1
        if otp_data["attempts"] >= 3:
            del otp_store[verification.email]
            raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new OTP")
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Mark user as verified in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_detailed SET is_verified = TRUE WHERE email = ?",
        (verification.email,)
    )
    conn.commit()
    conn.close()

    # Clear OTP
    del otp_store[verification.email]

    # Generate login token
    access_token = create_jwt_token({"sub": verification.email})

    response = JSONResponse(
        status_code=200,
        content={
            "message": "Email verified successfully. You can now log in.",
            "access_token": access_token
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response

async def login(request: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user
    cursor.execute(
        "SELECT password, is_verified FROM user_detailed WHERE email = ?",
        (request.email,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not pwd_context.verify(request.password, user[0]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # if not user[1]:  # Check if email is verified
    #     raise HTTPException(status_code=400, detail="Please verify your email before logging in")

    # Generate access token
    access_token = create_jwt_token({"sub": request.email})
    
    response = JSONResponse(
        status_code=200,
        content={
            "message": "Login successful",
            "access_token": access_token
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response

async def resend_otp(email: EmailStr):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists and needs verification
    cursor.execute(
        "SELECT is_verified FROM user_detailed WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    if user[0]:  # If already verified
        raise HTTPException(status_code=400, detail="Email is already verified")

    # Generate new OTP
    otp = generate_otp()
    otp_store[email] = {
        "otp": otp,
        "timestamp": datetime.utcnow(),
        "attempts": 0
    }

    # Send new OTP
    await send_email(
        email,
        "New verification code",
        f"Your new verification code is: {otp}. Valid for 5 minutes."
    )

    return {"status_code":200,"message": "New verification code sent to your email"}



def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") 
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


conn = sqlite3.connect("link.db", check_same_thread=False)
cursor = conn.cursor()

def forgot_generate_otp():
    """Generate a random 3-digit OTP (like Google)."""
    return str(random.randint(10000, 99999))

def store_otp(email: str, otp: str):
    """Store the OTP in the database."""
    cursor.execute("UPDATE user_detailed SET otp = ? WHERE email = ?", (otp, email))
    conn.commit()

def forgot_verify_otp(email: str, entered_otp: str) -> bool:
    """Check if the OTP matches the one stored in the database."""
    correct_otp = cursor.execute("SELECT otp FROM user_detailed WHERE email = ?", (email,)).fetchone()

    # Ensure correct_otp is not None before accessing index 0
    return correct_otp is not None and entered_otp == str(correct_otp[0])


def update_password(email: str, new_password: str):
    """Update the user's password in the database after hashing it."""
    hashed_password = pwd_context.hash(new_password)

    # Check if the email exists
    user_exists = cursor.execute("SELECT email FROM user_detailed WHERE email = ?", (email,)).fetchone()
    if not user_exists:
        print("Email not found in database.")
        return False  # Return False to indicate failure

    try:
        cursor.execute("UPDATE user_detailed SET password = ? WHERE email = ?", (hashed_password, email))
        conn.commit()
        return True  # Success
    except Exception as e:
        print("Error updating password:", e)
        return False  # Failure


def check_email_exists(email: str):
    """Check if the email exists in the user_detailed table."""
    result = cursor.execute("SELECT email FROM user_detailed WHERE email = ?", (email,)).fetchone()
    return result is not None
