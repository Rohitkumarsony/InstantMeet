from pydantic import BaseModel, EmailStr, validator
import re

class SignupRequest(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        # Ensure password and confirm_password match
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def validate_password_strength(cls, v):
        # Ensure password is at least 8 characters
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Ensure password contains at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Ensure password contains at least one number
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')

        # Optional: Ensure password contains at least one special character
        if not re.search(r'[\W_]', v):  # This matches non-word characters or underscores
            raise ValueError('Password must contain at least one special character')
        
        return v

    class Config:
        # Strip any leading/trailing whitespaces from string fields
        anystr_strip_whitespace = True


# Example OTP verification model
class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

# Example Login Request Model
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
# Pydantic model for resending OTP
class ResendOTPRequest(BaseModel):
    email: EmailStr
