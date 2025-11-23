import socketio
import json
import base64
import os
from datetime import datetime
from src.services.chat_services import ChatService

# Create a Socket.IO instance with increased max HTTP buffer size
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    max_http_buffer_size=100 * 1024 * 1024  # 100MB buffer for large files
)

# Initialize chat service
chat_service = ChatService()

def setup_socketio(app):
    @sio.event
    async def connect(sid, environ):
        print(f"Client connected: {sid}")

    @sio.event
    async def join(sid, data):
        username = data.get('username')
        if username:
            chat_service.add_user(sid, username)
            print(f"User {username} joined with SID: {sid}")
            
            # Send chat history to the new user
            for message in chat_service.get_chat_history():
                await sio.emit('chat_message', message, room=sid)
            
            # Send welcome message to the user
            welcome_message = {
                'username': 'System',
                'message': f'Welcome to the grouped chat, {username}!',
                'timestamp': datetime.now().strftime('%I:%M:%S %p')
            }
            await sio.emit('chat_message', welcome_message, room=sid)
            
            # Notify others that a new user joined
            join_notification = {
                'username': 'System',
                'message': f'{username} has joined the chat',
                'timestamp': datetime.now().strftime('%I:%M:%S %p')
            }
            await sio.emit('chat_message', join_notification, skip_sid=sid)
            
            # Send updated user list to all clients
            await sio.emit('user_list', {
                'users': chat_service.get_all_users()
            })

    @sio.event
    async def chat_message(sid, data):
        username = chat_service.get_username(sid)
        if username:
            try:
                # Save file if present
                if data.get('fileData') and data.get('fileType') and data.get('fileName'):
                    file_data = data['fileData']
                    
                    # If the file data is a base64 string, save it to disk
                    if ',' in file_data:  # Check if it's a base64 data URI
                        header, encoded = file_data.split(",", 1)
                        
                        try:
                            file_bytes = base64.b64decode(encoded)
                            
                            # Create a unique filename
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            file_name = f"{timestamp}_{data['fileName']}"
                            file_path = os.path.join("uploads", file_name)
                            
                            # Save the file
                            with open(file_path, "wb") as f:
                                f.write(file_bytes)
                            
                            # Replace the base64 data with the file path
                            data['fileData'] = f"/uploads/{file_name}"
                            print(f"File saved: {file_path}")
                        except Exception as e:
                            print(f"Error saving file: {e}")
                            # Continue with the message, but without the file
                            data.pop('fileData', None)
                            data.pop('fileType', None)
                            data.pop('fileName', None)
                            data['message'] = (data.get('message') or '') + " [File upload failed]"
                
                # Save the message to history
                chat_service.add_message(data)
                
                # Broadcast the message to all clients
                await sio.emit('chat_message', data)
            except Exception as e:
                print(f"Error processing message: {e}")
                error_message = {
                    'username': 'System',
                    'message': f"Error processing message: The file may be too large",
                    'timestamp': datetime.now().strftime('%I:%M:%S %p')
                }
                await sio.emit('chat_message', error_message, room=sid)

    @sio.event
    async def disconnect(sid):
        username = chat_service.remove_user(sid)
        if username:
            print(f"User {username} disconnected")
            
            # Notify others that a user left
            leave_notification = {
                'username': 'System',
                'message': f'{username} has left the chat',
                'timestamp': datetime.now().strftime('%I:%M:%S %p')
            }
            await sio.emit('chat_message', leave_notification)
            
            # Send updated user list to all clients
            await sio.emit('user_list', {
                'users': chat_service.get_all_users()
            })

    # Mount the Socket.IO app
    return socketio.ASGIApp(sio, app)