from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request,Form,Depends,Query,Path
import uuid
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.services.meeting_service import create_meeting_link,validate_meeting_link,get_db_connection,fetch_users_by_meeting_link
from src.services.login_service import templates
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse, HTMLResponse,JSONResponse
import asyncio
from src.router.login_router import get_user_from_session

meeting_router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# WebSocket Clients
connected_clients: Dict[str, WebSocket] = {}

# WebSocket API
@meeting_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())
    connected_clients[client_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "create_link":
                response = await create_meeting_link()
                await websocket.send_json(response)
            elif message["type"] == "validate_link":
                response = validate_meeting_link(message["link"])
                await websocket.send_json(response)
            else:
                await websocket.send_json({"type": "error", "message": "Unknown message type"})
    except WebSocketDisconnect:
        del connected_clients[client_id]
    except Exception as e:
        print(f"WebSocket error: {e}")

@meeting_router.post('/user-validate-and-save-in-db')
def validate_meeting_link_with_username(link: str, name: str) -> dict:
    """Validates meeting link and inserts new user details without modifying existing ones"""
    match = re.match(r"https://meet\.meeting.com/([0-9a-fA-F-]{36})", link)
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

        # Check if the meeting link exists
        cursor.execute("SELECT link, user_details FROM meeting_links WHERE uuid = ?", (extracted_uuid,))
        result = cursor.fetchone()
    
        if result and result[0] == link:
            existing_user_details = result[1]

            # ✅ Parse user_details correctly (convert dict to list if necessary)
            if existing_user_details:
                try:
                    user_details = json.loads(existing_user_details)
                    # Convert dictionary to list if it was stored incorrectly
                    if isinstance(user_details, dict):
                        user_details = [user_details]  # Convert single object to a list
                except json.JSONDecodeError:
                    user_details = []
            else:
                user_details = []

            # ✅ Always insert a new user as a separate entry
            new_user = {"name": name, "join_time": datetime_now()}
            user_details.append(new_user)  # ✅ Fix: Append to a list, not a dictionary

            # Convert back to JSON
            user_details_json = json.dumps(user_details)

            # ✅ Insert the new JSON data into the table
            cursor.execute("""
                UPDATE meeting_links 
                SET user_details = ? 
                WHERE uuid = ? AND link = ?
            """, (user_details_json, extracted_uuid, link))

            conn.commit()  # ✅ Ensure commit is called

            return {
                "type": "validate_link_response",
                "status": "success",
                "valid": True,
                "meeting_link": result[0],
                "user_details": user_details
            }
        else:
            return {
                "type": "validate_link_response",
                "status": "error",
                "valid": False,
                "message": "This link is not valid"
            }

def datetime_now():
    """Returns the current local timestamp in SQLite format"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')")
        return cursor.fetchone()[0]
    
@meeting_router.get("/meeting")  # Change to GET method
def join_meeting(request: Request, link: str):
    user_email = get_user_from_session(request)
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("meeting.html", {"request": request, "link": link})


@meeting_router.get("/grouped_meeting")
async def join_meeting(request: Request, link: str = Query(...)):
    user_email = get_user_from_session(request)
    logger.info(f"Session user: {user_email}")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    logger.info(f"Received request with username: {request}, link: {link}")
    """Serve the meeting page and pass validated users."""
    user_data = fetch_users_by_meeting_link(link)
    print(user_data)
    if not user_data["valid"]:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": user_data["message"]
        })

    return FileResponse("static/grouped_meeting.html")

active_connections = {}

async def notify_users(meeting_link: str):
    """Broadcast updated user list to all active WebSocket connections."""
    users_data = fetch_users_by_meeting_link(meeting_link)
    users = users_data["users"] if users_data["valid"] else []

    if meeting_link in active_connections:
        for connection in active_connections[meeting_link]:
            try:
                await connection.send_json({"type": "user_list", "users": users})
            except Exception as e:
                print(f"Error sending update: {e}")

@meeting_router.websocket("/ws/meeting")
async def websocket_endpoint(websocket: WebSocket, meeting_link: str = Query(...)):
    """WebSocket endpoint to manage real-time participant updates."""
    await websocket.accept()

    if meeting_link not in active_connections:
        active_connections[meeting_link] = []

    active_connections[meeting_link].append(websocket)

    # Send initial user list
    await notify_users(meeting_link)

    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        active_connections[meeting_link].remove(websocket)
        if not active_connections[meeting_link]:
            del active_connections[meeting_link]  # Clean up if no active users
        await notify_users(meeting_link)  # Notify others that a user left
    except Exception as e:
        print(f"WebSocket error: {str(e)}")

@meeting_router.get("/api/active_users/")
async def get_active_users(meeting_link: str):
    """API to fetch active users in a meeting using query parameters."""
    users_data = fetch_users_by_meeting_link(meeting_link)
    users = users_data["users"] if users_data["valid"] else []
    return JSONResponse(content={"users": users})
