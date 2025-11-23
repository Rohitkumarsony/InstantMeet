def get_chat_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Group Chat Application</title>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 900px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                height: 90vh;
            }
            .header {
                padding: 15px;
                background: #4a69bd;
                color: white;
                border-radius: 10px 10px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .online-users {
                width: 200px;
                padding: 10px;
                background: #f8f9fa;
                border-right: 1px solid #ddd;
                overflow-y: auto;
            }
            .chat-container {
                display: flex;
                flex: 1;
                overflow: hidden;
            }
            .chat-window {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            .message {
                margin-bottom: 15px;
                max-width: 80%;
            }
            .message-content {
                padding: 10px;
                border-radius: 10px;
                word-wrap: break-word;
            }
            .message-sender {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .my-message {
                align-self: flex-end;
            }
            .my-message .message-content {
                background-color: #4a69bd;
                color: white;
            }
            .other-message {
                align-self: flex-start;
            }
            .other-message .message-content {
                background-color: #e9ecef;
            }
            .system-message {
                align-self: center;
                max-width: 90%;
            }
            .system-message .message-content {
                background-color: #ffc107;
                color: #333;
                text-align: center;
            }
            .message-image {
                max-width: 100%;
                max-height: 200px;
                border-radius: 5px;
                cursor: pointer;
            }
            .message-video {
                max-width: 100%;
                max-height: 300px;
                border-radius: 5px;
            }
            .input-area {
                display: flex;
                padding: 15px;
                border-top: 1px solid #ddd;
                background: #f8f9fa;
                align-items: center;
            }
            .message-input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-right: 10px;
            }
            .send-btn, .file-btn {
                padding: 10px 15px;
                background: #4a69bd;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .file-btn {
                margin-right: 10px;
                position: relative;
                overflow: hidden;
            }
            .file-input {
                position: absolute;
                top: 0;
                left: 0;
                opacity: 0;
                width: 100%;
                height: 100%;
                cursor: pointer;
            }
            .login-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            .login-box {
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                width: 300px;
            }
            .login-input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .login-btn {
                padding: 10px 20px;
                background: #4a69bd;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
            }
            .file-preview {
                margin-top: 10px;
                text-align: center;
            }
            #preview-image, #preview-video {
                max-width: 100%;
                max-height: 200px;
                display: none;
                margin: 10px 0;
            }
            .timestamp {
                font-size: 0.8em;
                color: #888;
                margin-top: 5px;
            }
            .file-size-warning {
                color: red;
                font-size: 0.8em;
                display: none;
                margin-top: 5px;
            }
            .sending-indicator {
                display: none;
                align-self: center;
                color: #666;
                margin: 10px 0;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Group Chat</h1>
                <span id="username-display"></span>
            </div>
            <div class="chat-container">
                <div class="online-users">
                    <h3>Online Users</h3>
                    <ul id="users-list"></ul>
                </div>
                <div class="chat-window" id="chat-window">
                    <div class="sending-indicator" id="sending-indicator">Sending file, please wait...</div>
                </div>
            </div>
            <div class="input-area">
                <button class="file-btn">
                    <input type="file" class="file-input" id="file-input" accept="image/*,video/*">
                    Upload
                </button>
                <input type="text" class="message-input" id="message-input" placeholder="Type your message...">
                <button class="send-btn" id="send-btn">Send</button>
            </div>
            <div class="file-preview">
                <img id="preview-image" src="" alt="Preview">
                <video id="preview-video" controls></video>
                <div id="file-size-warning" class="file-size-warning">
                    Warning: Large files may cause issues. Maximum recommended size is 10MB.
                </div>
            </div>
        </div>

        <div class="login-overlay" id="login-overlay">
            <div class="login-box">
                <h2>Enter Your Username</h2>
                <input type="text" class="login-input" id="username-input" placeholder="Username">
                <button class="login-btn" id="login-btn">Join Chat</button>
            </div>
        </div>

        <script>
            // Variables
            let socket;
            let currentUsername = '';
            let selectedFile = null;
            let isSending = false;
            const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
            
            // DOM elements
            const loginOverlay = document.getElementById('login-overlay');
            const usernameInput = document.getElementById('username-input');
            const loginBtn = document.getElementById('login-btn');
            const usernameDisplay = document.getElementById('username-display');
            const usersList = document.getElementById('users-list');
            const chatWindow = document.getElementById('chat-window');
            const messageInput = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');
            const fileInput = document.getElementById('file-input');
            const previewImage = document.getElementById('preview-image');
            const previewVideo = document.getElementById('preview-video');
            const fileSizeWarning = document.getElementById('file-size-warning');
            const sendingIndicator = document.getElementById('sending-indicator');
            
            // Check if the user was already logged in (from sessionStorage)
            window.addEventListener('load', () => {
                const savedUsername = sessionStorage.getItem('username');
                if (savedUsername) {
                    currentUsername = savedUsername;
                    initializeChat(currentUsername);
                }
            });
            
            // Login button click event
            loginBtn.addEventListener('click', () => {
                const username = usernameInput.value.trim();
                if (username) {
                    currentUsername = username;
                    sessionStorage.setItem('username', username);
                    initializeChat(username);
                }
            });
            
            // Enter key to login
            usernameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    loginBtn.click();
                }
            });
            
            function initializeChat(username) {
                // Hide login overlay
                loginOverlay.style.display = 'none';
                
                // Display username
                usernameDisplay.textContent = `Logged in as: ${username}`;
                
                // Initialize Socket.IO connection with larger timeout
                socket = io({
                    reconnectionDelay: 1000,
                    reconnectionDelayMax: 5000,
                    timeout: 60000,  // 60 second timeout
                });
                
                // Socket.IO events
                socket.on('connect', () => {
                    console.log('Connected to server');
                    // Join the chat with username
                    socket.emit('join', { username });
                });
                
                socket.on('user_list', (data) => {
                    updateUsersList(data.users);
                });
                
                socket.on('chat_message', (data) => {
                    displayMessage(data);
                    
                    // If it was our message and sending indicator is shown, hide it
                    if (isSending && data.username === currentUsername) {
                        isSending = false;
                        sendingIndicator.style.display = 'none';
                    }
                });
                
                socket.on('connect_error', (error) => {
                    console.error('Connection error:', error);
                    displaySystemMessage("Connection error. Please refresh the page.");
                });
                
                socket.on('disconnect', () => {
                    console.log('Disconnected from server');
                    displaySystemMessage("Disconnected from server. Trying to reconnect...");
                });
                
                // Send button click event
                sendBtn.addEventListener('click', sendMessage);
                
                // Enter key to send message
                messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
                
                // File input change event
                fileInput.addEventListener('change', handleFileSelect);
            }
            
            function sendMessage() {
                if (isSending) return; // Prevent sending multiple files at once
                
                const messageText = messageInput.value.trim();
                
                if (messageText || selectedFile) {
                    const timestamp = new Date().toLocaleTimeString();
                    
                    if (selectedFile) {
                        // Show sending indicator
                        isSending = true;
                        sendingIndicator.style.display = 'block';
                        
                        const reader = new FileReader();
                        reader.onload = function(event) {
                            const fileData = event.target.result;
                            const fileType = selectedFile.type.startsWith('image/') ? 'image' : 'video';
                            
                            socket.emit('chat_message', {
                                username: currentUsername,
                                message: messageText,
                                fileData: fileData,
                                fileType: fileType,
                                fileName: selectedFile.name,
                                timestamp: timestamp
                            });
                            
                            // Clear file preview
                            previewImage.style.display = 'none';
                            previewVideo.style.display = 'none';
                            previewImage.src = '';
                            previewVideo.src = '';
                            fileSizeWarning.style.display = 'none';
                            selectedFile = null;
                        };
                        
                        // If there's an error reading the file
                        reader.onerror = function(error) {
                            console.error('Error reading file:', error);
                            displaySystemMessage("Error reading file. Please try again with a different file.");
                            isSending = false;
                            sendingIndicator.style.display = 'none';
                        };
                        
                        reader.readAsDataURL(selectedFile);
                    } else {
                        socket.emit('chat_message', {
                            username: currentUsername,
                            message: messageText,
                            timestamp: timestamp
                        });
                    }
                    
                    // Clear message input
                    messageInput.value = '';
                }
            }
            
            function handleFileSelect(event) {
                selectedFile = event.target.files[0];
                
                if (selectedFile) {
                    const fileURL = URL.createObjectURL(selectedFile);
                    
                    // Check file size and show warning for large files
                    if (selectedFile.size > MAX_FILE_SIZE) {
                        fileSizeWarning.style.display = 'block';
                    } else {
                        fileSizeWarning.style.display = 'none';
                    }
                    
                    if (selectedFile.type.startsWith('image/')) {
                        previewImage.src = fileURL;
                        previewImage.style.display = 'block';
                        previewVideo.style.display = 'none';
                    } else if (selectedFile.type.startsWith('video/')) {
                        previewVideo.src = fileURL;
                        previewVideo.style.display = 'block';
                        previewImage.style.display = 'none';
                    }
                }
            }
            
            function displayMessage(data) {
                const messageDiv = document.createElement('div');
                
                // Determine message class
                let messageClass = 'message ';
                if (data.username === 'System') {
                    messageClass += 'system-message';
                } else if (data.username === currentUsername) {
                    messageClass += 'my-message';
                } else {
                    messageClass += 'other-message';
                }
                
                messageDiv.className = messageClass;
                
                let messageHTML = `
                    <div class="message-sender">${data.username}</div>
                    <div class="message-content">
                `;
                
                if (data.message) {
                    messageHTML += `<p>${data.message}</p>`;
                }
                
                if (data.fileData && data.fileType) {
                    if (data.fileType === 'image') {
                        messageHTML += `<img src="${data.fileData}" class="message-image" alt="Shared image" onclick="openFullscreen(this)">`;
                    } else if (data.fileType === 'video') {
                        messageHTML += `<video controls class="message-video" src="${data.fileData}"></video>`;
                    }
                }
                
                messageHTML += `
                    <div class="timestamp">${data.timestamp}</div>
                    </div>
                `;
                
                messageDiv.innerHTML = messageHTML;
                chatWindow.appendChild(messageDiv);
                
                // Scroll to bottom
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
            
            function displaySystemMessage(message) {
                const timestamp = new Date().toLocaleTimeString();
                displayMessage({
                    username: 'System',
                    message: message,
                    timestamp: timestamp
                });
            }
            
            function updateUsersList(users) {
                usersList.innerHTML = '';
                users.forEach(user => {
                    const li = document.createElement('li');
                    li.textContent = user;
                    usersList.appendChild(li);
                });
            }
            
            function openFullscreen(element) {
                if (element.requestFullscreen) {
                    element.requestFullscreen();
                } else if (element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if (element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }
            }
        </script>
    </body>
    </html>
    """