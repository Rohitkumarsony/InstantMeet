from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uuid
import re
from typing import Dict,Optional
import logging
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.db import get_db_connection
import json

app = FastAPI()

# Mount the static directory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_meeting_link() -> dict:
    unique_id = str(uuid.uuid4())
    meeting_link = f"https://meet.meeting.com/{unique_id}"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO meeting_links (uuid, link, type) VALUES (?, ?, ?)",
            (unique_id, meeting_link, "admin")
        )
        conn.commit()
    
    return {
        "type": "create_link_response",
        "status": "success",
        "meeting_link": meeting_link
    }

def validate_meeting_link(link: str) -> dict:
    match = re.match(r"https://meet\.meeting\.com/([0-9a-fA-F-]{36})", link)
    if not match:
        return {
            "type": "validate_link_response",
            "status": "error",
            "valid": False,
            "message": "Invalid link format"
        }
    
    extracted_uuid = match.group(1)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT link FROM meeting_links WHERE uuid = ?", (extracted_uuid,))
        result = cursor.fetchone()
    
    if result and result[0] == link:
        return {
            "type": "validate_link_response",
            "status": "success",
            "valid": True,
            "meeting_link": result[0]
        }
    else:
        return {
            "type": "validate_link_response",
            "status": "error",
            "valid": False,
            "message": "This link is not valid"
        }
        
        
# def fetch_users_by_meeting_link(link: str) -> dict:
#     """Fetch all users associated with a valid meeting link UUID."""
#     match = re.match(r"https://meet\.meeting\.com/([0-9a-fA-F-]{36})", link)
#     if not match:
#         return {
#             "type": "fetch_users_response",
#             "status": "error",
#             "valid": False,
#             "message": "Invalid link format"
#         }

#     extracted_uuid = match.group(1)

#     with get_db_connection() as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT user_details FROM meeting_links WHERE uuid = ?", (extracted_uuid,))
#         result = cursor.fetchone()

#     if result:
#         try:
#             users = json.loads(result[0])  # Assuming user_details is stored as a JSON array
#         except json.JSONDecodeError:
#             users = []

#         return {
#             "type": "fetch_users_response",
#             "status": "success",
#             "valid": True,
#             "users": users
#         }
#     else:
#         return {
#             "type": "fetch_users_response",
#             "status": "error",
#             "valid": False,
#             "message": "Meeting not found"
#         }


def fetch_users_by_meeting_link(link: str) -> dict:
    """Fetch all users associated with a valid meeting link UUID."""
    match = re.match(r"https://meet\.meeting\.com/([0-9a-fA-F-]{36})", link)
    if not match:
        return {
            "type": "fetch_users_response",
            "status": "error",
            "valid": False,
            "message": "Invalid link format"
        }

    extracted_uuid = match.group(1)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_details FROM meeting_links WHERE uuid = ?", (extracted_uuid,))
        result = cursor.fetchone()

    if result:
        try:
            users = json.loads(result[0])  # Assuming user_details is stored as a JSON array
        except json.JSONDecodeError:
            users = []

        return {
            "type": "fetch_users_response",
            "status": "success",
            "valid": True,
            "users": users,
            "meeting_uuid": extracted_uuid
        }
    else:
        return {
            "type": "fetch_users_response",
            "status": "error",
            "valid": False,
            "message": "Meeting not found"
        }
