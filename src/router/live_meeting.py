# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime
# from typing import Dict, List, Optional
# import socketio
# import logging
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles

# live_meeting_router = FastAPI()

# # Mount the static directory
# live_meeting_router.mount("/static", StaticFiles(directory="static"), name="static")

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # WebSocket Clients
# connected_clients: Dict[str, WebSocket] = {}
# rooms = {}

# # Socket.IO Setup with optimized configuration for UDP/WebRTC
# sio = socketio.AsyncServer(
#     async_mode='asgi',
#     cors_allowed_origins='*',
#     ping_timeout=20000,  # Increased for better WebRTC stability
#     ping_interval=5000,  # Increased interval
#     max_http_buffer_size=1e7
# )

# # Create ASGI app with the correct order
# socket_app = socketio.ASGIApp(
#     socketio_server=sio,
#     other_asgi_app=live_meeting_router
# )

# # Store active users
# rooms = {}  # {room_id: [users]}


# @sio.event
# async def connect(sid, environ):
#     logger.info(f"User {sid} connected")


# @sio.event
# async def join_room(sid, data):
#     try:
#         room = data.get('room')
#         username = data.get('username')
        
#         if not room or not username:
#             logger.error("Join room error: Missing room or username")
#             return  # Avoid proceeding with None values

#         if room not in rooms:
#             rooms[room] = []
            
#         # Add user to room
#         rooms[room].append({'sid': sid, 'username': username})

#         # ⚠️ Remove `await` because `sio.enter_room()` is not async
#         sio.enter_room(sid, room)

#         logger.info(f"{username} joined room {room}")
        
#         # Notify everyone about user list
#         await sio.emit("user_list", rooms[room], room=room)
        
#         # Notify others about new user (for WebRTC connection)
#         for user in rooms[room]:
#             if user['sid'] != sid:
#                 await sio.emit('user_joined', {
#                     'sid': sid,
#                     'username': username
#                 }, room=user['sid'])
                
#     except KeyError as e:
#         logger.error(f"Join room error: Missing data - {str(e)}")
#     except Exception as e:
#         logger.error(f"Join room error: {str(e)}")


# @sio.event
# async def leave_room(sid, data):
#     try:
#         room = data['room']
#         # Remove user from room
#         rooms[room] = [user for user in rooms[room] if user['sid'] != sid]
#         await sio.leave_room(sid, room)
        
#         # Notify others
#         await sio.emit("user_list", rooms[room], room=room)
#         await sio.emit("user_disconnected", sid, room=room)
        
#     except Exception as e:
#         logger.error(f"Leave room error: {str(e)}")

# @sio.event
# async def offer(sid, data):
#     try:
#         # Include UDP preference in offer configuration
#         await sio.emit('offer', {
#             'offer': data['offer'],
#             'from': sid,
#             'username': next((user['username'] for user in rooms[data['room']] if user['sid'] == sid), None),
#             'room': data['room']
#         }, room=data['to'])
#     except Exception as e:
#         logger.error(f"Offer error: {str(e)}")

# @sio.event
# async def answer(sid, data):
#     try:
#         await sio.emit('answer', {
#             'answer': data['answer'],
#             'from': sid,
#             'room': data['room']
#         }, room=data['to'])
#     except Exception as e:
#         logger.error(f"Answer error: {str(e)}")

# @sio.event
# async def ice_candidate(sid, data):
#     try:
#         # Forward ICE candidates (includes UDP candidates)
#         await sio.emit('ice_candidate', {
#             'candidate': data['candidate'],
#             'from': sid,
#             'room': data['room']
#         }, room=data['to'])
#     except Exception as e:
#         logger.error(f"ICE candidate error: {str(e)}")

# @sio.event
# async def start_screen_share(sid, data):
#     try:
#         room = data['room']
#         await sio.emit("screen_share_started", {'sid': sid}, room=room, skip_sid=sid)
#     except Exception as e:
#         logger.error(f"Start screen share error: {str(e)}")

# @sio.event
# async def stop_screen_share(sid, data):
#     try:
#         room = data['room']
#         await sio.emit("screen_share_stopped", room=room)
#     except Exception as e:
#         logger.error(f"Stop screen share error: {str(e)}")

# @sio.event
# async def disconnect(sid):
#     try:
#         # Find and remove user from all rooms
#         for room_id, room_users in rooms.items():
#             rooms[room_id] = [user for user in room_users if user['sid'] != sid]
#             if room_users != rooms[room_id]:  # If user was in this room
#                 await sio.emit("user_list", rooms[room_id], room=room_id)
#                 await sio.emit("user_disconnected", sid, room=room_id)
        
#         logger.info(f"User {sid} disconnected")
#     except Exception as e:
#         logger.error(f"Disconnect error: {str(e)}")

# # Use the socket_app as the main application
# live_meeting_router = socket_app






# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from datetime import datetime
# from typing import Dict, List, Optional
# import socketio
# import logging

# # Initialize FastAPI app
# live_meeting_router = FastAPI()

# # Mount the static directory
# live_meeting_router.mount("/static", StaticFiles(directory="static"), name="static")

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Store active users in rooms
# rooms: Dict[str, List[Dict[str, str]]] = {}  # {room_id: [{"sid": sid, "username": username}]}

# # Socket.IO setup optimized for WebRTC
# sio = socketio.AsyncServer(
#     async_mode="asgi",
#     cors_allowed_origins="*",
#     ping_timeout=20000,
#     ping_interval=5000,
#     max_http_buffer_size=int(1e7),
# )

# # Create ASGI app for Socket.IO
# socket_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=live_meeting_router)


# @sio.event
# async def connect(sid, environ):
#     logger.info(f"User {sid} connected")


# @sio.event
# async def join_room(sid, data):
#     try:
#         room = data.get("room")
#         username = data.get("username")

#         if not room or not username:
#             logger.error("Join room error: Missing room or username")
#             return

#         if room not in rooms:
#             rooms[room] = []

#         # Prevent duplicate entries
#         if any(user["sid"] == sid for user in rooms[room]):
#             return

#         # Add user to room
#         rooms[room].append({"sid": sid, "username": username})
#         sio.enter_room(sid, room)  # No `await` needed

#         logger.info(f"{username} joined room {room}")

#         # Notify everyone in the room about the updated user list
#         await sio.emit("user_list", rooms[room], room=room)

#         # Notify other users about the new participant
#         for user in rooms[room]:
#             if user["sid"] != sid:
#                 await sio.emit("user_joined", {"sid": sid, "username": username}, room=user["sid"])

#     except Exception as e:
#         logger.error(f"Join room error: {str(e)}")


# @sio.event
# async def leave_room(sid, data):
#     try:
#         room = data.get("room")
#         if not room or room not in rooms:
#             return

#         # Remove user from the room
#         rooms[room] = [user for user in rooms[room] if user["sid"] != sid]
#         await sio.leave_room(sid, room)

#         # Notify remaining users
#         await sio.emit("user_list", rooms[room], room=room)
#         await sio.emit("user_disconnected", {"sid": sid}, room=room)

#         # Remove empty rooms
#         if not rooms[room]:
#             del rooms[room]

#     except Exception as e:
#         logger.error(f"Leave room error: {str(e)}")


# @sio.event
# async def offer(sid, data):
#     try:
#         room = data.get("room")
#         target_sid = data.get("to")
#         offer = data.get("offer")

#         if room not in rooms:
#             return

#         sender_username = next((user["username"] for user in rooms[room] if user["sid"] == sid), None)

#         await sio.emit(
#             "offer",
#             {"offer": offer, "from": sid, "username": sender_username, "room": room},
#             room=target_sid,
#         )
#     except Exception as e:
#         logger.error(f"Offer error: {str(e)}")


# @sio.event
# async def answer(sid, data):
#     try:
#         room = data.get("room")
#         target_sid = data.get("to")
#         answer = data.get("answer")

#         await sio.emit("answer", {"answer": answer, "from": sid, "room": room}, room=target_sid)
#     except Exception as e:
#         logger.error(f"Answer error: {str(e)}")


# @sio.event
# async def ice_candidate(sid, data):
#     try:
#         room = data.get("room")
#         target_sid = data.get("to")
#         candidate = data.get("candidate")

#         await sio.emit("ice_candidate", {"candidate": candidate, "from": sid, "room": room}, room=target_sid)
#     except Exception as e:
#         logger.error(f"ICE candidate error: {str(e)}")


# @sio.event
# async def start_screen_share(sid, data):
#     try:
#         room = data.get("room")
#         await sio.emit("screen_share_started", {"sid": sid}, room=room, skip_sid=sid)
#     except Exception as e:
#         logger.error(f"Start screen share error: {str(e)}")


# @sio.event
# async def stop_screen_share(sid, data):
#     try:
#         room = data.get("room")
#         await sio.emit("screen_share_stopped", room=room)
#     except Exception as e:
#         logger.error(f"Stop screen share error: {str(e)}")


# @sio.event
# async def disconnect(sid):
#     try:
#         # Find and remove user from all rooms
#         for room in list(rooms.keys()):  # Copy keys to avoid runtime modification issues
#             rooms[room] = [user for user in rooms[room] if user["sid"] != sid]
#             if not rooms[room]:  # Remove empty rooms
#                 del rooms[room]

#         # Notify all rooms
#         for room_id, room_users in rooms.items():
#             await sio.emit("user_list", room_users, room=room_id)
#             await sio.emit("user_disconnected", {"sid": sid}, room=room_id)

#         logger.info(f"User {sid} disconnected")
#     except Exception as e:
#         logger.error(f"Disconnect error: {str(e)}")


# # Use socket_app as the main application
# live_meeting_router = socket_app








import os
import socketio
import logging
import ffmpeg  # Requires `pip install ffmpeg-python`
from fastapi import FastAPI
from datetime import datetime

# Initialize FastAPI and Socket.IO
app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to save recordings
SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)

# Store active users in rooms
rooms = {}  # {room_id: [{"sid": sid, "username": username}]}
recordings = {}  # {room_id: {"chunks": [], "filename": "room1234.webm"}}


@sio.event
async def connect(sid, environ):
    logger.info(f"User {sid} connected")


@sio.event
async def join_room(sid, data):
    try:
        room = data.get("room")
        username = data.get("username")

        if not room or not username:
            logger.error("Join room error: Missing room or username")
            return

        if room not in rooms:
            rooms[room] = []

        # Prevent duplicate entries
        if any(user["sid"] == sid for user in rooms[room]):
            return

        # Add user to room
        rooms[room].append({"sid": sid, "username": username})
        sio.enter_room(sid, room)

        logger.info(f"{username} joined room {room}")

        # Notify everyone about the updated user list
        await sio.emit("user_list", rooms[room], room=room)

        # Notify others about the new participant
        for user in rooms[room]:
            if user["sid"] != sid:
                await sio.emit("user_joined", {"sid": sid, "username": username}, room=user["sid"])

    except Exception as e:
        logger.error(f"Join room error: {str(e)}")


@sio.event
async def leave_room(sid, data):
    try:
        room = data.get("room")
        if not room or room not in rooms:
            return

        # Remove user from room
        rooms[room] = [user for user in rooms[room] if user["sid"] != sid]
        await sio.leave_room(sid, room)

        # Notify remaining users
        await sio.emit("user_list", rooms[room], room=room)
        await sio.emit("user_disconnected", {"sid": sid}, room=room)

        # Remove empty rooms
        if not rooms[room]:
            del rooms[room]

    except Exception as e:
        logger.error(f"Leave room error: {str(e)}")


@sio.event
async def offer(sid, data):
    try:
        room = data.get("room")
        target_sid = data.get("to")
        offer = data.get("offer")

        if room not in rooms:
            return

        sender_username = next((user["username"] for user in rooms[room] if user["sid"] == sid), None)

        await sio.emit(
            "offer",
            {"offer": offer, "from": sid, "username": sender_username, "room": room},
            room=target_sid,
        )
    except Exception as e:
        logger.error(f"Offer error: {str(e)}")


@sio.event
async def answer(sid, data):
    try:
        room = data.get("room")
        target_sid = data.get("to")
        answer = data.get("answer")

        await sio.emit("answer", {"answer": answer, "from": sid, "room": room}, room=target_sid)
    except Exception as e:
        logger.error(f"Answer error: {str(e)}")


@sio.event
async def ice_candidate(sid, data):
    try:
        room = data.get("room")
        target_sid = data.get("to")
        candidate = data.get("candidate")

        await sio.emit("ice_candidate", {"candidate": candidate, "from": sid, "room": room}, room=target_sid)
    except Exception as e:
        logger.error(f"ICE candidate error: {str(e)}")


@sio.event
async def start_screen_share(sid, data):
    try:
        room = data.get("room")
        await sio.emit("screen_share_started", {"sid": sid}, room=room, skip_sid=sid)
    except Exception as e:
        logger.error(f"Start screen share error: {str(e)}")


@sio.event
async def stop_screen_share(sid, data):
    try:
        room = data.get("room")
        await sio.emit("screen_share_stopped", room=room)
    except Exception as e:
        logger.error(f"Stop screen share error: {str(e)}")


@sio.event
async def disconnect(sid):
    try:
        # Find and remove user from all rooms
        for room in list(rooms.keys()):
            rooms[room] = [user for user in rooms[room] if user["sid"] != sid]
            if not rooms[room]:
                del rooms[room]

        # Notify all rooms
        for room_id, room_users in rooms.items():
            await sio.emit("user_list", room_users, room=room_id)
            await sio.emit("user_disconnected", {"sid": sid}, room=room_id)

        logger.info(f"User {sid} disconnected")
    except Exception as e:
        logger.error(f"Disconnect error: {str(e)}")



# Use socket_app as the main application
live_meeting_router = socket_app





















# from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Query
# from fastapi.middleware.cors import CORSMiddleware
# import socketio
# import logging
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from src.db import save_user_info, get_db_connection

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Create FastAPI router
# meeting_router = APIRouter()

# # Create templates (assuming you have a templates directory)
# templates = Jinja2Templates(directory="templates")

# # Socket.IO Setup - specify async_mode as 'asgi'
# sio = socketio.AsyncServer(
#     async_mode='asgi',
#     cors_allowed_origins="*",
#     logger=True,
#     engineio_logger=True
# )

# # Create ASGI app with the correct order
# socket_app = socketio.ASGIApp(
#     socketio_server=sio,
#     other_asgi_app=meeting_router
# )

# # Store active users and rooms
# rooms = {}  # {room_id: [users]}
# user_info = {}  # {user_id: {name, room}}

# def normalize_meeting_id(meeting_id):
#     """Normalize meeting ID to ensure consistency."""
#     if not meeting_id:
#         return ""
#     # Remove path prefixes if present (handle both /room/xyz and xyz formats)
#     if "/" in meeting_id:
#         meeting_id = meeting_id.split("/")[-1]
#     # Remove any query parameters if present
#     if "?" in meeting_id:
#         meeting_id = meeting_id.split("?")[0]
#     return meeting_id.strip().lower()

# @sio.event
# async def connect(sid, environ):
#     """Handle new socket connection."""
#     logger.info(f"User {sid} connected")
#     return True

# @sio.event
# async def join_meeting(sid, data):
#     """Handle user joining a meeting."""
#     try:
#         original_meeting_id = data.get('meetingId', '')
#         # Normalize meeting ID to ensure consistency
#         meeting_id = normalize_meeting_id(original_meeting_id)
#         user_id = data.get('userId', '').strip()
#         user_name = data.get('userName', 'Anonymous')

#         logger.info(f"Joining meeting: Original ID '{original_meeting_id}', Normalized ID '{meeting_id}'")

#         if not meeting_id or not user_id:
#             logger.error("Join meeting error: Missing meeting_id or user_id")
#             return
        
#         # Ensure a consistent room exists
#         if meeting_id not in rooms:
#             rooms[meeting_id] = []
#             logger.info(f"Created new meeting room: {meeting_id}")

#         # Check if user is already in the room
#         existing_user = next((u for u in rooms[meeting_id] if u["userId"] == user_id), None)
#         if existing_user:
#             logger.info(f"User {user_name} (ID: {user_id}) is already in meeting {meeting_id}")
#         else:
#             # Add new user to the meeting
#             user_data = {
#                 "userId": user_id,
#                 "userName": user_name,
#                 "isAudioMuted": True,
#                 "isVideoOff": True
#             }
#             rooms[meeting_id].append(user_data)

#         # Store user session info
#         user_info[user_id] = {
#             "sid": sid,
#             "userName": user_name,
#             "meetingId": meeting_id
#         }
        
#         conn = get_db_connection()
#         if conn is None:
#             logger.error("Database connection failed.")
#         else:
#             save_user_info(user_id, meeting_id, user_info)

#         # Join the correct Socket.IO room
#         await sio.enter_room(sid, meeting_id)
#         logger.info(f"User {user_name} (ID: {user_id}) joined meeting {meeting_id}")
        
#         # Log current room status
#         logger.info(f"Room {meeting_id} now has {len(rooms[meeting_id])} users")

#         # Notify all users in the room about the updated user list
#         await sio.emit("user_list", {"users": rooms[meeting_id]}, room=meeting_id)

#         # Notify others that a new user has joined
#         for user in rooms[meeting_id]:
#             if user["userId"] != user_id:
#                 user_sid = user_info.get(user["userId"], {}).get("sid")
#                 if user_sid:
#                     await sio.emit("user_joined", {
#                         "userId": user_id,
#                         "userName": user_name
#                     }, room=user_sid)
                
#                 # Notify the new user about existing users
#                 await sio.emit("user_joined", {
#                     "userId": user["userId"],
#                     "userName": user["userName"]
#                 }, room=sid)

#     except Exception as e:
#         logger.error(f"Join meeting error: {str(e)}")


# @sio.event
# async def leave_meeting(sid, data):
#     """Handle user leaving a meeting."""
#     try:
#         user_id = data.get('userId', '')
#         meeting_id = normalize_meeting_id(data.get('meetingId', ''))
        
#         if meeting_id in rooms:
#             # Remove user from room
#             rooms[meeting_id] = [user for user in rooms[meeting_id] if user["userId"] != user_id]
            
#             # Leave the socket room
#             await sio.leave_room(sid, meeting_id)
#             logger.info(f"User {user_id} left meeting {meeting_id}")
            
#             # Clean up user info
#             if user_id in user_info:
#                 del user_info[user_id]
            
#             # Notify others about the user leaving
#             await sio.emit("user_list", {"users": rooms[meeting_id]}, room=meeting_id)
#             await sio.emit("user_left", {"userId": user_id}, room=meeting_id)
    
#     except Exception as e:
#         logger.error(f"Leave meeting error: {str(e)}")


# @sio.event
# async def offer(sid, data):
#     """Handle WebRTC offer."""
#     try:
#         to_user_id = data.get('to', '')
#         to_sid = user_info.get(to_user_id, {}).get("sid", "")
        
#         if to_sid:
#             await sio.emit("offer", {
#                 "from": data.get('from', sid),
#                 "offer": data.get('offer', {})
#             }, room=to_sid)
#         else:
#             logger.warning(f"Offer: Cannot find user {to_user_id}")
    
#     except Exception as e:
#         logger.error(f"Offer error: {str(e)}")


# @sio.event
# async def answer(sid, data):
#     """Handle WebRTC answer."""
#     try:
#         to_user_id = data.get('to', '')
#         to_sid = user_info.get(to_user_id, {}).get("sid", "")
        
#         if to_sid:
#             await sio.emit("answer", {
#                 "from": data.get('from', sid),
#                 "answer": data.get('answer', {})
#             }, room=to_sid)
#         else:
#             logger.warning(f"Answer: Cannot find user {to_user_id}")
    
#     except Exception as e:
#         logger.error(f"Answer error: {str(e)}")


# @sio.event
# async def ice_candidate(sid, data):
#     """Handle ICE candidate."""
#     try:
#         to_user_id = data.get('to', '')
#         to_sid = user_info.get(to_user_id, {}).get("sid", "")
        
#         if to_sid:
#             await sio.emit("ice_candidate", {
#                 "from": data.get('from', sid),
#                 "candidate": data.get('candidate', {})
#             }, room=to_sid)
#         else:
#             logger.warning(f"ICE candidate: Cannot find user {to_user_id}")
    
#     except Exception as e:
#         logger.error(f"ICE candidate error: {str(e)}")


# @sio.event
# async def media_state_change(sid, data):
#     """Handle media state changes (mute/unmute, video on/off)."""
#     try:
#         user_id = data.get('userId', '')
#         is_audio_muted = data.get('isAudioMuted', True)
#         is_video_off = data.get('isVideoOff', True)
        
#         # Find user's meeting
#         meeting_id = user_info.get(user_id, {}).get("meetingId", "")
        
#         if meeting_id and meeting_id in rooms:
#             # Update user's media state
#             for user in rooms[meeting_id]:
#                 if user["userId"] == user_id:
#                     user["isAudioMuted"] = is_audio_muted
#                     user["isVideoOff"] = is_video_off
#                     break
            
#             # Notify everyone in the room about the change
#             await sio.emit("media_state_changed", {
#                 "userId": user_id,
#                 "isAudioMuted": is_audio_muted,
#                 "isVideoOff": is_video_off
#             }, room=meeting_id)
    
#     except Exception as e:
#         logger.error(f"Media state change error: {str(e)}")


# @sio.event
# async def get_user_info(sid, data, callback=None):
#     """Get information about a specific user."""
#     try:
#         user_id = data.get('userId', '')
        
#         # Find user info
#         for meeting_id, users in rooms.items():
#             for user in users:
#                 if user["userId"] == user_id:
#                     user_data = {
#                         "userId": user_id,
#                         "userName": user["userName"],
#                         "isAudioMuted": user.get("isAudioMuted", True),
#                         "isVideoOff": user.get("isVideoOff", True)
#                     }
                    
#                     if callback:
#                         callback(user_data)
#                     return
        
#         # User not found
#         if callback:
#             callback({"userId": user_id, "userName": "Unknown User"})
    
#     except Exception as e:
#         logger.error(f"Get user info error: {str(e)}")
#         if callback:
#             callback({"error": str(e)})


# @sio.event
# async def disconnect(sid):
#     """Handle socket disconnection."""
#     try:
#         # Find user associated with this sid
#         found_user_id = None
#         found_meeting_id = None
        
#         for user_id, data in user_info.items():
#             if data.get("sid") == sid:
#                 found_user_id = user_id
#                 found_meeting_id = data.get("meetingId")
#                 break
        
#         # If found, remove from meeting
#         if found_user_id and found_meeting_id and found_meeting_id in rooms:
#             # Remove user from room
#             rooms[found_meeting_id] = [
#                 user for user in rooms[found_meeting_id] 
#                 if user["userId"] != found_user_id
#             ]
            
#             # Clean up user info
#             if found_user_id in user_info:
#                 del user_info[found_user_id]
            
#             # Notify others
#             await sio.emit("user_list", {"users": rooms[found_meeting_id]}, room=found_meeting_id)
#             await sio.emit("user_left", {"userId": found_user_id}, room=found_meeting_id)
            
#             logger.info(f"User {found_user_id} disconnected from meeting {found_meeting_id}")
        
#         logger.info(f"User with socket {sid} disconnected")
    
#     except Exception as e:
#         logger.error(f"Disconnect error: {str(e)}")


# live_meeting_router = socket_app



















# from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Query
# from fastapi.middleware.cors import CORSMiddleware
# import socketio
# import logging
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from src.db import save_user_info,get_db_connection


# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Create FastAPI router
# meeting_router = APIRouter()

# # Create templates (assuming you have a templates directory)
# templates = Jinja2Templates(directory="templates")

# # Socket.IO Setup - specify async_mode as 'asgi'
# sio = socketio.AsyncServer(
#     async_mode='asgi',
#     cors_allowed_origins="*",
#     logger=True,
#     engineio_logger=True
# )

# # Create ASGI app with the correct order
# socket_app = socketio.ASGIApp(
#     socketio_server=sio,
#     other_asgi_app=meeting_router
# )

# # Store active users and rooms
# rooms = {}  # {room_id: [users]}
# user_info = {}  # {user_id: {name, room}}



# @sio.event
# async def connect(sid, environ):
#     """Handle new socket connection."""
#     logger.info(f"User {sid} connected")
#     return True

# @sio.event
# async def join_meeting(sid, data):
#     """Handle user joining a meeting."""
#     try:
#         meeting_id = data.get('meetingId', '').strip().lower()  # Normalize meeting ID
#         user_id = data.get('userId', '').strip()
#         user_name = data.get('userName', 'Anonymous')

#         if not meeting_id or not user_id:
#             logger.error("Join meeting error: Missing meeting_id or user_id")
#             return
        
#         # Ensure a consistent room exists
#         if meeting_id not in rooms:
#             rooms[meeting_id] = []

#         # Check if user is already in the room
#         existing_user = next((u for u in rooms[meeting_id] if u["userId"] == user_id), None)
#         if existing_user:
#             logger.info(f"User {user_name} (ID: {user_id}) is already in meeting {meeting_id}")
#         else:
#             # Add new user to the meeting
#             user_data = {
#                 "userId": user_id,
#                 "userName": user_name,
#                 "isAudioMuted": True,
#                 "isVideoOff": True
#             }
#             rooms[meeting_id].append(user_data)

#         # Store user session info
#         user_info[user_id] = {
#             "sid": sid,
#             "userName": user_name,
#             "meetingId": meeting_id
#         }
        
#         conn = get_db_connection()
#         if conn is None:
#             logger.error("Database connection failed.")
#             return

#         save_user_info(user_id, meeting_id, user_info)

#         # Join the correct Socket.IO room
#         await sio.enter_room(sid, meeting_id)
#         logger.info(f"User {user_name} (ID: {user_id}) joined meeting {meeting_id}")

#         # Notify all users in the room about the updated user list
#         await sio.emit("user_list", {"users": rooms[meeting_id]}, room=meeting_id)

#         # Notify others that a new user has joined
#         for user in rooms[meeting_id]:
#             if user["userId"] != user_id:
#                 user_sid = user_info.get(user["userId"], {}).get("sid")
#                 if user_sid:
#                     await sio.emit("user_joined", {
#                         "userId": user_id,
#                         "userName": user_name
#                     }, room=user_sid)
                
#                 # Notify the new user about existing users
#                 await sio.emit("user_joined", {
#                     "userId": user["userId"],
#                     "userName": user["userName"]
#                 }, room=sid)

#     except Exception as e:
#         logger.error(f"Join meeting error: {str(e)}")


# @sio.event
# async def leave_meeting(sid, data):
#     """Handle user leaving a meeting."""
#     try:
#         user_id = data.get('userId', '')
#         meeting_id = data.get('meetingId', '')
        
#         if meeting_id in rooms:
#             # Remove user from room
#             rooms[meeting_id] = [user for user in rooms[meeting_id] if user["userId"] != user_id]
            
#             # Leave the socket room
#             await sio.leave_room(sid, meeting_id)
#             logger.info(f"User {user_id} left meeting {meeting_id}")
            
#             # Clean up user info
#             if user_id in user_info:
#                 del user_info[user_id]
            
#             # Notify others about the user leaving
#             await sio.emit("user_list", {"users": rooms[meeting_id]}, room=meeting_id)
#             await sio.emit("user_left", {"userId": user_id}, room=meeting_id)
    
#     except Exception as e:
#         logger.error(f"Leave meeting error: {str(e)}")


# @sio.event
# async def offer(sid, data):
#     """Handle WebRTC offer."""
#     try:
#         to_user_id = data.get('to', '')
#         to_sid = user_info.get(to_user_id, {}).get("sid", "")
        
#         if to_sid:
#             await sio.emit("offer", {
#                 "from": data.get('from', sid),
#                 "offer": data.get('offer', {})
#             }, room=to_sid)
#         else:
#             logger.warning(f"Offer: Cannot find user {to_user_id}")
    
#     except Exception as e:
#         logger.error(f"Offer error: {str(e)}")


# @sio.event
# async def answer(sid, data):
#     """Handle WebRTC answer."""
#     try:
#         to_user_id = data.get('to', '')
#         to_sid = user_info.get(to_user_id, {}).get("sid", "")
        
#         if to_sid:
#             await sio.emit("answer", {
#                 "from": data.get('from', sid),
#                 "answer": data.get('answer', {})
#             }, room=to_sid)
#         else:
#             logger.warning(f"Answer: Cannot find user {to_user_id}")
    
#     except Exception as e:
#         logger.error(f"Answer error: {str(e)}")


# @sio.event
# async def ice_candidate(sid, data):
#     """Handle ICE candidate."""
#     try:
#         to_user_id = data.get('to', '')
#         to_sid = user_info.get(to_user_id, {}).get("sid", "")
        
#         if to_sid:
#             await sio.emit("ice_candidate", {
#                 "from": data.get('from', sid),
#                 "candidate": data.get('candidate', {})
#             }, room=to_sid)
#         else:
#             logger.warning(f"ICE candidate: Cannot find user {to_user_id}")
    
#     except Exception as e:
#         logger.error(f"ICE candidate error: {str(e)}")


# @sio.event
# async def media_state_change(sid, data):
#     """Handle media state changes (mute/unmute, video on/off)."""
#     try:
#         user_id = data.get('userId', '')
#         is_audio_muted = data.get('isAudioMuted', True)
#         is_video_off = data.get('isVideoOff', True)
        
#         # Find user's meeting
#         meeting_id = user_info.get(user_id, {}).get("meetingId", "")
        
#         if meeting_id and meeting_id in rooms:
#             # Update user's media state
#             for user in rooms[meeting_id]:
#                 if user["userId"] == user_id:
#                     user["isAudioMuted"] = is_audio_muted
#                     user["isVideoOff"] = is_video_off
#                     break
            
#             # Notify everyone in the room about the change
#             await sio.emit("media_state_changed", {
#                 "userId": user_id,
#                 "isAudioMuted": is_audio_muted,
#                 "isVideoOff": is_video_off
#             }, room=meeting_id)
    
#     except Exception as e:
#         logger.error(f"Media state change error: {str(e)}")


# @sio.event
# async def get_user_info(sid, data, callback=None):
#     """Get information about a specific user."""
#     try:
#         user_id = data.get('userId', '')
        
#         # Find user info
#         for meeting_id, users in rooms.items():
#             for user in users:
#                 if user["userId"] == user_id:
#                     user_data = {
#                         "userId": user_id,
#                         "userName": user["userName"],
#                         "isAudioMuted": user.get("isAudioMuted", True),
#                         "isVideoOff": user.get("isVideoOff", True)
#                     }
                    
#                     if callback:
#                         callback(user_data)
#                     return
        
#         # User not found
#         if callback:
#             callback({"userId": user_id, "userName": "Unknown User"})
    
#     except Exception as e:
#         logger.error(f"Get user info error: {str(e)}")
#         if callback:
#             callback({"error": str(e)})


# @sio.event
# async def disconnect(sid):
#     """Handle socket disconnection."""
#     try:
#         # Find user associated with this sid
#         found_user_id = None
#         found_meeting_id = None
        
#         for user_id, data in user_info.items():
#             if data.get("sid") == sid:
#                 found_user_id = user_id
#                 found_meeting_id = data.get("meetingId")
#                 break
        
#         # If found, remove from meeting
#         if found_user_id and found_meeting_id and found_meeting_id in rooms:
#             # Remove user from room
#             rooms[found_meeting_id] = [
#                 user for user in rooms[found_meeting_id] 
#                 if user["userId"] != found_user_id
#             ]
            
#             # Clean up user info
#             if found_user_id in user_info:
#                 del user_info[found_user_id]
            
#             # Notify others
#             await sio.emit("user_list", {"users": rooms[found_meeting_id]}, room=found_meeting_id)
#             await sio.emit("user_left", {"userId": found_user_id}, room=found_meeting_id)
        
#         logger.info(f"User with socket {sid} disconnected")
    
#     except Exception as e:
#         logger.error(f"Disconnect error: {str(e)}")


# live_meeting_router = socket_app





# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# import sqlite3
# import uuid
# import json
# import re
# from datetime import datetime
# from typing import Dict, List, Optional
# import socketio
# import logging
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# from src.services.login_service import templates
# from fastapi.templating import Jinja2Templates

# live_meeting_router= FastAPI()


# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# templates = Jinja2Templates(directory="templates")

# # WebSocket Clients
# connected_clients: Dict[str, WebSocket] = {}
# rooms = {}
# print('rohit',rooms)

# # Socket.IO Setup - specify async_mode as 'asgi'
# # # Socket.IO Setup - specify async_mode as 'asgi'
# sio = socketio.AsyncServer(
#     async_mode='asgi',
#     cors_allowed_origins="*",
#     logger=True,
#     engineio_logger=True
# )

# # Create ASGI app with the correct order
# socket_app = socketio.ASGIApp(
#     socketio_server=sio,
#     other_asgi_app=live_meeting_router
# )

# # Store active users
# # rooms = {}  # {room_id: [users]}

# @sio.event
# async def connect(sid, environ):
#     logger.info(f"User {sid} connected")

# @sio.event
# async def join_room(sid, data):
#     try:
#         room = data['room']
#         username = data['username']
        
#         if room not in rooms:
#             rooms[room] = []
            
#         # Add user to room
#         rooms[room].append({'sid': sid, 'username': username})
#         await sio.enter_room(sid, room)
#         logger.info(f"{username} joined room {room}")
        
#         # Notify everyone about user list
#         await sio.emit("user_list", rooms[room], room=room)
        
#         # Notify others about new user (for WebRTC connection)
#         for user in rooms[room]:
#             if user['sid'] != sid:
#                 await sio.emit('user_joined', {
#                     'sid': sid,
#                     'username': username
#                 }, room=user['sid'])
                
#     except KeyError as e:
#         logger.error(f"Join room error: Missing data - {str(e)}")
#     except Exception as e:
#         logger.error(f"Join room error: {str(e)}")

# @sio.event
# async def leave_room(sid, data):
#     try:
#         room = data['room']
#         # Remove user from room
#         rooms[room] = [user for user in rooms[room] if user['sid'] != sid]
#         await sio.leave_room(sid, room)
        
#         # Notify others
#         await sio.emit("user_list", rooms[room], room=room)
#         await sio.emit("user_disconnected", sid, room=room)
        
#     except Exception as e:
#         logger.error(f"Leave room error: {str(e)}")

# @sio.event
# async def offer(sid, data):
#     try:
#         await sio.emit('offer', {
#             'offer': data['offer'],
#             'from': sid,
#             'username': next((user['username'] for user in rooms[data['room']] if user['sid'] == sid), None),
#             'room': data['room']
#         }, room=data['to'])
#     except Exception as e:
#         logger.error(f"Offer error: {str(e)}")

# @sio.event
# async def answer(sid, data):
#     try:
#         await sio.emit('answer', {
#             'answer': data['answer'],
#             'from': sid,
#             'room': data['room']
#         }, room=data['to'])
#     except Exception as e:
#         logger.error(f"Answer error: {str(e)}")

# @sio.event
# async def ice_candidate(sid, data):
#     try:
#         await sio.emit('ice_candidate', {
#             'candidate': data['candidate'],
#             'from': sid,
#             'room': data['room']
#         }, room=data['to'])
#     except Exception as e:
#         logger.error(f"ICE candidate error: {str(e)}")

# @sio.event
# async def start_screen_share(sid, data):
#     try:
#         room = data['room']
#         await sio.emit("screen_share_started", {'sid': sid}, room=room, skip_sid=sid)
#     except Exception as e:
#         logger.error(f"Start screen share error: {str(e)}")

# @sio.event
# async def stop_screen_share(sid, data):
#     try:
#         room = data['room']
#         await sio.emit("screen_share_stopped", room=room)
#     except Exception as e:
#         logger.error(f"Stop screen share error: {str(e)}")

# @sio.event
# async def disconnect(sid):
#     try:
#         # Find and remove user from all rooms
#         for room_id, room_users in rooms.items():
#             rooms[room_id] = [user for user in room_users if user['sid'] != sid]
#             if room_users != rooms[room_id]:  # If user was in this room
#                 await sio.emit("user_list", rooms[room_id], room=room_id)
#                 await sio.emit("user_disconnected", sid, room=room_id)
        
#         logger.info(f"User {sid} disconnected")
#     except Exception as e:
#         logger.error(f"Disconnect error: {str(e)}")

# # Use the socket_app as the main application
# live_meeting_router= socket_app