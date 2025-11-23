from fastapi import FastAPI, Request, Response
from starlette.middleware.sessions import SessionMiddleware  
from starlette.middleware.cors import CORSMiddleware
import os
from src.router.login_router import api_router
from dotenv import load_dotenv
from src.router.meeting_router import meeting_router
from src.router.live_meeting import live_meeting_router
from fastapi.staticfiles import StaticFiles
from src.router.chat_router import router
from src.services.chat_services_socket import setup_socketio
import uvicorn

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',  # Specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Add SessionMiddleware for session handling
SECRET_KEY = os.getenv("SECRET_KEY")  # Ensure you set a secret key
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Include your API router
app.include_router(api_router)
app.include_router(meeting_router)

app.mount("/", live_meeting_router)










# from fastapi import FastAPI
# from starlette.middleware.sessions import SessionMiddleware  
# from starlette.middleware.cors import CORSMiddleware
# import os
# import uvicorn
# from dotenv import load_dotenv

# from src.router.login_router import api_router
# from src.router.meeting_router import meeting_router
# from src.router.live_meeting import live_meeting_router  # Likely an ASGI app
# from src.router.chat_router import router
# from src.services.chat_services_socket import setup_socketio
# from fastapi.staticfiles import StaticFiles

# # Load environment variables
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI()

# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"],  
#     allow_headers=["*"],  
# )

# # Ensure SECRET_KEY is set
# SECRET_KEY = os.getenv("SECRET_KEY")
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY is not set in the environment variables!")

# # Add SessionMiddleware for session handling
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# # Create 'uploads' directory if it doesn't exist
# uploads_dir = os.path.join(os.getcwd(), "uploads")
# os.makedirs(uploads_dir, exist_ok=True)

# # Mount the static directory for uploads
# app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# # Include API routers
# app.include_router(api_router)
# app.include_router(meeting_router)
# app.include_router(router)

# # ✅ Correctly mount `live_meeting_router` as an ASGI app
# app.mount("/", live_meeting_router)
# # app.mount("/", router)  

# # Setup Socket.IO integration
# app = setup_socketio(app)  

# # Run the application
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)



# from fastapi import FastAPI
# from starlette.middleware.sessions import SessionMiddleware  
# from starlette.middleware.cors import CORSMiddleware
# import os
# import uvicorn
# from dotenv import load_dotenv

# from src.router.login_router import api_router
# from src.router.meeting_router import meeting_router
# from src.router.live_meeting import live_meeting_router  # Likely an ASGI app
# from src.router.chat_router import router  # Chat router import
# from src.services.chat_services_socket import setup_socketio
# from fastapi.staticfiles import StaticFiles

# # Load environment variables
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI()

# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"],  
#     allow_headers=["*"],  
# )

# # Ensure SECRET_KEY is set
# SECRET_KEY = os.getenv("SECRET_KEY")
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY is not set in the environment variables!")

# # Add SessionMiddleware for session handling
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# # Create 'uploads' directory if it doesn't exist
# uploads_dir = os.path.join(os.getcwd(), "uploads")
# os.makedirs(uploads_dir, exist_ok=True)

# # Mount the static directory for uploads
# app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# # Include API routers
# app.include_router(api_router)
# app.include_router(meeting_router)

# # Mount chat router on a distinct path
# app.include_router(router, prefix="/chat")  # Mount chat router under /chat

# # Correctly mount `live_meeting_router` as an ASGI app on a distinct path
# app.mount("/live_meeting", live_meeting_router)  # Mount live meeting on /live_meeting

# # Setup Socket.IO integration
# app = setup_socketio(app)  

# # Run the application
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
