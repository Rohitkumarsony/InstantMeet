# import sqlite3
# import json
# # Database initialization (same as before)
# # Database initialization (same as before)
# def create_db():
#     conn = sqlite3.connect("link.db")
#     cursor = conn.cursor()
    
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS user_detailed (
#             uuid TEXT PRIMARY KEY,
#             firstname TEXT NOT NULL,
#             lastname TEXT NOT NULL,
#             email TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             is_verified BOOLEAN DEFAULT FALSE,
#             account_create_time TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
#             login_time TEXT DEFAULT '[]',
#             otp INTEGER
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS meeting_links (
#             uuid TEXT PRIMARY KEY,
#             link TEXT NOT NULL,
#             type TEXT NOT NULL,
#             user_details TEXT DEFAULT '[]',
#             admin_email TEXT,
#             admin_password TEXT,
#             admin_phone_number TEXT
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS meeting_data (
#             uuid TEXT PRIMARY KEY,
#             link TEXT NOT NULL,
#             user_details TEXT DEFAULT '[]',
#             user_email TEXT,
#             user_password TEXT,
#             meeting_endtime TEXT
#         ) 
#     """)

#     # FIXED user_info table (removed the trailing comma)
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS user_info (
#         userId TEXT NOT NULL,
#         meetingId TEXT NOT NULL,
#         user_details TEXT DEFAULT '[]',
#         PRIMARY KEY (userId, meetingId)
#     )
        
#     """)

#     conn.commit()
#     conn.close()

    
# # Utility Functions
# def get_db_connection():
#     return sqlite3.connect("link.db", check_same_thread=False)



# conn = sqlite3.connect("link.db")
# cursor = conn.cursor()
    


# def save_user_info(user_id: str, meeting_id: str, user_details: dict):
#     """Save or update user info in the database."""
#     try:
#         user_details_json = json.dumps(user_details)  # Convert dict to JSON string

#         # Use INSERT OR REPLACE with correct composite primary key
#         query = """
#             INSERT INTO user_info (userId, meetingId, user_details)
#             VALUES (?, ?, ?)
#             ON CONFLICT(userId, meetingId) DO UPDATE SET 
#                 user_details = excluded.user_details
#         """
#         cursor.execute(query, (user_id, meeting_id, user_details_json))
#         conn.commit()
#         print(f"User {user_id} saved/updated successfully in meeting {meeting_id}.")
    
#     except Exception as e:
#         print(f"Error saving user info: {e}")
#         conn.rollback()


import sqlite3
import json
from loguru import logger

# Database initialization
def create_db():
    conn = sqlite3.connect("link.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_detailed (
            uuid TEXT PRIMARY KEY,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_verified BOOLEAN DEFAULT FALSE,
            account_create_time TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
            login_time TEXT DEFAULT '[]',
            otp INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_links (
            uuid TEXT PRIMARY KEY,
            link TEXT NOT NULL,
            type TEXT NOT NULL,
            user_details TEXT DEFAULT '[]',
            admin_email TEXT,
            admin_password TEXT,
            admin_phone_number TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_data (
            uuid TEXT PRIMARY KEY,
            link TEXT NOT NULL,
            user_details TEXT DEFAULT '[]',
            user_email TEXT,
            user_password TEXT,
            meeting_endtime TEXT
        ) 
    """)

    # FIXED user_info table (removed the trailing comma)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_info (
            userId TEXT NOT NULL,
            meetingId TEXT NOT NULL,
            user_details TEXT DEFAULT '[]',
            PRIMARY KEY (userId, meetingId)
        )
    """)

    conn.commit()
    conn.close()

# Utility Functions
def get_db_connection():
    try:
        return sqlite3.connect("link.db", check_same_thread=False)
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def save_user_info(user_id: str, meeting_id: str, user_details: dict):
    """Save or update user info in the database."""
    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        user_details_json = json.dumps(user_details)  # Convert dict to JSON string

        query = """
            INSERT INTO user_info (userId, meetingId, user_details)
            VALUES (?, ?, ?)
            ON CONFLICT(userId, meetingId) DO UPDATE SET 
                user_details = excluded.user_details
        """
        cursor.execute(query, (user_id, meeting_id, user_details_json))
        conn.commit()
        logger.info(f"User {user_id} saved/updated successfully in meeting {meeting_id}.")
    
    except Exception as e:
        logger.error(f"Error saving user info: {e}")
        conn.rollback()
    
    finally:
        conn.close()
