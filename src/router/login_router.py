import os
import uuid
from fastapi import APIRouter, Request, Form, Response, HTTPException,Depends,Query
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
import redis
from datetime import timedelta
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse, HTMLResponse
# Import service functions and models
from src.services.login_service import signup, verify_otp, login, resend_otp,update_password,check_email_exists,send_email,forgot_verify_otp,forgot_generate_otp,store_otp,generate_otp,validate_name,validate_password
from src.models.login_models import SignupRequest, LoginRequest, OTPVerification,ResendOTPRequest
import hashlib
import json
from src.db import get_db_connection

# Initialize the API api_router
api_router = APIRouter()

# Initialize Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Configuration (SECRET_KEY should ideally be pulled from environment variables in production)
SECRET_KEY = os.getenv("SECRET_KEY")

# Redis Client Setup (for session management)
redis_client = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,  # Ensures responses are returned as strings instead of bytes
    socket_timeout=5,  # Optional: Prevents long hangs in case Redis is unresponsive
    socket_connect_timeout=5,  # Optional: Prevents long hangs during initial connection
)

COOKIE_NAME = "session_id"

def create_session(response: Response, user_email: str, request: Request):
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    user_agent = request.headers.get("User-Agent", "")
    
    session_data = {
        "email": user_email,
        "hash": hashlib.sha256(user_agent.encode()).hexdigest()
    }
    
    redis_client.set(session_id, json.dumps(session_data), ex=timedelta(days=15))  # Store session in Redis
    
    response.set_cookie(
        COOKIE_NAME, session_id, httponly=True, secure=True, samesite="Lax"
    )

def validate_session(request: Request) -> bool:
    session_id = request.cookies.get(COOKIE_NAME)
    
    if not session_id:
        return False
    
    session_data = redis_client.get(session_id)
    
    if session_data:
        try:
            stored_data = json.loads(session_data)  # Parse JSON data
            user_agent = request.headers.get("User-Agent", "")
            
            if stored_data["hash"] == hashlib.sha256(user_agent.encode()).hexdigest():
                return True
        except json.JSONDecodeError:
            return False  # Handle JSON decoding issues
    
    return False

# Function to retrieve user email from session
def get_user_from_session(request: Request):
    session_id = request.cookies.get(COOKIE_NAME)
    
    if not session_id:
        return None
    
    session_data = redis_client.get(session_id)
    
    if session_data:
        try:
            stored_data = json.loads(session_data)  # Decode JSON
            return stored_data.get("email")  # Return the email
        except json.JSONDecodeError:
            return None  # Handle corrupted data
    
    return None

# Route for home page (root)
@api_router.get("/")
async def get_home(request: Request,current_user: str = Depends(get_user_from_session)):
    if current_user:  # If session exists, redirect to welcome page
        return RedirectResponse("/welcome", status_code=303)

    # If no session exists (user is not logged in), render the home page
    return templates.TemplateResponse("home.html", {"request": request})


# Route for serving the signup page (GET request)
@api_router.get("/signup")
async def get_signup(request: Request):
    # Check if the user is already logged in by checking the session
    user_email = get_user_from_session(request)
    
    if user_email:
        # If a session exists (user is logged in), redirect directly to the welcome page
        return RedirectResponse("/welcome", status_code=303)
    
    # If no session exists (user is not logged in), render the signup page
    return templates.TemplateResponse("signup.html", {"request": request})

# Route for user signup (POST request)
@api_router.post("/signup")
async def user_signup(
    request: Request,
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    signup_data = SignupRequest(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=password,
        confirm_password=confirm_password,
    )
        
    # email_validation=await check_email_exists_or_not(email)
    signup_result = await signup(signup_data)

    if signup_result.status_code == 200:
        # Redirect to OTP verification page
        return templates.TemplateResponse("verify_otp.html", {"request": request, "email": email})
    else:
        return JSONResponse(
            status_code=401,
            content={"error": "Signup failed. Please try again."}
        )
        
        

@api_router.get("/check-email")
async def check_email(email: str = Query(...)):
    """Check if an email already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user_detailed WHERE email = ?", (email,))
    exists = cursor.fetchone()
    conn.close()
    
    return {"exists": bool(exists)}


# Route for OTP verification
@api_router.post("/verify-otp")
async def user_verify_otp(
    email: EmailStr = Form(...),
    otp: str = Form(...),
    request: Request = None
):
    verification_data = OTPVerification(email=email, otp=otp)
    verification_result = await verify_otp(verification_data)

    if verification_result.status_code == 200:
        # If OTP is valid, redirect to login page
        return templates.TemplateResponse("login.html", {"request": request, "email": email})
    else:
        # Show error message if OTP is invalid
        return templates.TemplateResponse("verify_otp.html", {"request": request, "email": email, "error": "Invalid OTP. Please try again."})

# Route for serving the login page (GET request)
@api_router.get("/login")
async def get_login(request: Request):
    # Check if the user is already logged in by checking the session
    user_email = get_user_from_session(request)
    
    if user_email:
        # If a session exists (user is logged in), redirect directly to the welcome page
        return RedirectResponse("/welcome", status_code=303)
    
    # If no session exists (user is not logged in), render the login page
    return templates.TemplateResponse("login.html", {"request": request})


@api_router.post("/login")
async def user_login(
    email: EmailStr = Form(...),
    password: str = Form(...),
    request: Request = None  # ✅ Ensure request is passed
):
    login_data = LoginRequest(email=email, password=password)
    login_result = await login(login_data)

    if login_result.status_code == 200:
        # Create session and redirect to welcome page
        response = RedirectResponse("/welcome", status_code=303)
        create_session(response, email, request)  # ✅ Now passing 'request' correctly
        return response
    else:
        return JSONResponse(status_code=401, content={"message": "Invalid credentials"})


# Route for serving the welcome page after login
@api_router.get("/welcome")
async def get_welcome(request: Request):
    user_email = get_user_from_session(request)
    if user_email is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return templates.TemplateResponse("welcome.html", {"request": request, "user_email": user_email})


# POST route to handle OTP resending
@api_router.post("/resend-otp")
async def user_resend_otp(request: Request, body: ResendOTPRequest):
    # Validate the email is in the request body
    if not body.email:
        raise HTTPException(status_code=400, detail="Email is required")

    # Call your resend_otp function (you should replace this with actual OTP logic)
    result = await resend_otp(body.email)

    if result:
        return JSONResponse(content=result, status_code=200)
    else:
        raise HTTPException(status_code=500, detail="Failed to resend OTP. Please try again.")



@api_router.get("/logout")
async def logout(request: Request):
    # Retrieve the session ID from cookies
    session_id = request.cookies.get(COOKIE_NAME)

    # Create a response object to remove the cookie
    response = RedirectResponse("/", status_code=303)  # Redirect to home or login page
    
    if session_id:
        try:
            redis_client.delete(session_id)  # Remove session from Redis
        except Exception as e:
            print(f"Redis error: {e}")  # Log error (use loguru/logger in production)

    response.delete_cookie(COOKIE_NAME)  # Remove the session cookie

    return response


@api_router.post("/send-otp/")
async def send_otp(email: str = Form(...)):
    """Check if email exists, then generate and send OTP."""
    
    # Check if the email exists in the database
    if not check_email_exists(email):
        return JSONResponse(content={"error": "Email not found"}, status_code=404)
    
    # Generate and store OTP
    otp = forgot_generate_otp()
    store_otp(email, otp)

    # Send OTP email
    await send_email(
        email,
        "Verify your email",
        f"Your verification code is: {otp}. Valid for 5 minutes."
    )

    # Return a JSON response instead of a redirect
    return JSONResponse(content={"success": True, "email": email})


@api_router.get('/forgot-password')
def forget_password(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@api_router.get("/verify-otp-forget-password", response_class=HTMLResponse)
async def verify_otp_page(request: Request, email: str):
    """Render the OTP verification page."""
    return templates.TemplateResponse("forget_password_verifyopt.html", {"request": request, "email": email})

@api_router.post("/validate-otp/")
async def validate_otp(email: str = Form(...), otp: str = Form(...)):
    """Validate OTP and redirect to password reset page."""
    print(email,otp)
    if forgot_verify_otp(email, otp):
        return JSONResponse(content={"success": True, "email": email})
        # return RedirectResponse(url=f"/reset-password?email={email}", status_code=303)
    return RedirectResponse(url=f"/verify-otp-forget-password?email={email}&error=Invalid OTP", status_code=303)

@api_router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, email: str):
    """Render the password reset page."""
    return templates.TemplateResponse("reset_password.html", {"request": request, "email": email})

@api_router.post("/update-password/")
async def update_password_route(email: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...)):
    """Update the user's password after successful OTP verification."""
    if new_password != confirm_password:
        return RedirectResponse(url=f"/reset-password?email={email}&error=Passwords do not match", status_code=303)

    success = update_password(email, new_password)
    print(success)
    if not success:
        return RedirectResponse(url=f"/reset-password?email={email}&error=Email not found", status_code=303)

    return RedirectResponse(url="/", status_code=303)
