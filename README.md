# InstantMeet

A real-time video meeting application built with FastAPI and WebRTC technology, providing seamless audio/video communication with low latency.

## 🚀 Features

- **Instant Meeting Creation**: Generate meeting links with a single click using the "Generate Link" button
- **Real-time Video Calling**: High-quality video conferencing using WebRTC
- **Audio Communication**: Crystal-clear audio streaming with UDP for minimal latency
- **Group Meetings**: Support for multiple participants in a single session
- **Chat Functionality**: Built-in text chat during meetings
- **User Authentication**: Secure login and signup system
- **Password Recovery**: Forgot password with OTP verification
- **Meeting Recordings**: Save your meetings for future reference

## 🛠️ Technology Stack

### Backend
- **Python** - Core programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLite** - Lightweight database for data persistence
- **Jinja2** - Template engine for HTML rendering
- **WebSocket** - Real-time bidirectional communication

### Frontend
- **HTML5** - Structure and layout
- **CSS3** - Styling and responsive design
- **JavaScript** - Client-side interactivity and WebRTC implementation

### Communication Protocol
- **UDP** - Optimal for real-time communication
- **WebRTC** - Peer-to-peer audio/video streaming
- **WebSocket** - For signaling and chat messages

## 📁 Project Structure

```
InstantMeet/
│
├── main.py                     # FastAPI main entry point
├── README.md                   # Project documentation
├── link.db                     # SQLite database
│
├── src/                        # Backend source code
│   ├── db.py                   # Database connection & session handler
│   │
│   ├── models/                 # Pydantic + ORM models
│   │   └── login_models.py
│   │
│   ├── router/                 # FastAPI routers
│   │   ├── chat_router.py
│   │   ├── live_meeting.py
│   │   ├── login_router.py
│   │   └── meeting_router.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── chat_services.py
│   │   ├── chat_services_socket.py
│   │   ├── login_service.py
│   │   └── meeting_service.py
│   │
│   └── templates.py            # Template response handler (Jinja2)
│
├── templates/                  # Frontend HTML Templates
│   ├── login.html
│   ├── signup.html
│   ├── home.html
│   ├── meeting.html
│   ├── grouped_meeting.html
│   ├── forgot_password.html
│   ├── forget_password_verifyopt.html
│   ├── reset_password.html
│   ├── verify_otp.html
│   └── welcome.html
│
├── static/                     # Client-side assets
│   ├── meeting.js              # WebRTC logic
│   └── grouped_meeting.html
│
├── recordings/                 # Meeting recordings storage
│
└── __pycache__/                # Python cache files
```

## 🚦 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Rohitkumarsony/InstantMeet.git
cd instantmeet
```

2. Create a virtual environment:
```bash
python3 -m venv env
```

3. Activate the virtual environment:

**On Linux/macOS:**
```bash
source env/bin/activate
```

**On Windows:**
```bash
env\Scripts\activate
```

4. Create a `.env` file in the project root:
```bash
# Create .env file
touch .env
```

Add the following configuration to your `.env` file:
```env
DATABASE_URL=sqlite:///./link.db
SECRET_KEY=your-secret-key-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

5. Install required dependencies:
```bash
pip install -r requirements.txt
```

6. Run the application:

**Option 1: Using Python directly**
```bash
uvicorn main:app --reload
```

**Option 2: Using Docker**
```bash
# Build the image
docker build -t instantmeet .

# Run the container
docker run -d -p 8000:8000 --name instantmeet_app instantmeet

# Stop the container
docker stop instantmeet_app

# Remove the container
docker rm instantmeet_app
```

7. Open your browser and navigate to:
```
http://localhost:8000
```

## 💡 How to Use

1. **Sign Up / Login**: Create an account or login with existing credentials
2. **Create Meeting**: Click on "Generate Link" button to create a new meeting room
3. **Share Link**: Copy the generated meeting link and share with participants
4. **Join Meeting**: Participants can join by clicking on the shared link
5. **Start Communicating**: Enable camera/microphone and start your video call
6. **Use Chat**: Send text messages during the meeting using the built-in chat
7. **Record (Optional)**: Save important meetings for later review

## 🌟 Key Features Explained

### Meeting Link Generation
- One-click meeting creation with "Generate Link" button
- Unique, shareable URLs for each meeting session
- No scheduling required - instant meetings on demand

### Real-Time Communication
- **UDP Protocol**: Ensures minimal latency for audio/video
- **WebRTC Technology**: Direct peer-to-peer connections
- **Low Latency Streaming**: Optimized for real-time interaction

### Security
- Password-protected user accounts
- OTP verification for password recovery
- Secure session management

## 🔧 Configuration

Database and server configurations can be modified in:
- `src/db.py` - Database settings
- `main.py` - Server and CORS settings

## 📝 API Endpoints

- `/` - Home page
- `/login` - User authentication
- `/signup` - User registration
- `/meeting` - Meeting room interface
- `/chat` - WebSocket chat endpoint
- `/generate-link` - Create new meeting link

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Developer

Built with ❤️ using Python, FastAPI, and WebRTC

## 📞 Support

For issues and questions, please open an issue in the GitHub repository.

---

**InstantMeet** - Connect Instantly, Meet Seamlessly
