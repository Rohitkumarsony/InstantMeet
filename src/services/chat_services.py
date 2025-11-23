import json
import os
from datetime import datetime

class ChatService:
    def __init__(self, max_history=1000):
        self.connected_users = {}  # sid -> username
        self.chat_history = []  # List to store chat messages
        self.max_history = max_history
        self.load_chat_history()
        
    def add_user(self, sid, username):
        self.connected_users[sid] = username
        
    def get_username(self, sid):
        return self.connected_users.get(sid)
        
    def remove_user(self, sid):
        return self.connected_users.pop(sid, None)
        
    def get_all_users(self):
        return list(self.connected_users.values())
    
    def add_message(self, message):
        self.chat_history.append(message)
        # Limit history size
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
        # Save to disk
        self.save_chat_history()
    
    def get_chat_history(self):
        return self.chat_history
    
    def save_chat_history(self):
        try:
            with open('chat_history.json', 'w') as f:
                json.dump(self.chat_history, f, indent=4)  # Add indent for readability
        except Exception as e:
            print(f"Error saving chat history: {e}")

    
    def load_chat_history(self):
        try:
            if os.path.exists('chat_history.json'):
                with open('chat_history.json', 'r') as f:
                    self.chat_history = json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
            self.chat_history = []