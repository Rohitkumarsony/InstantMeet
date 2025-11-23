const socket = io('http://localhost:8000', {
    transports: ['websocket'],
    upgrade: false // Prevent transport upgrade to polling
});
let localStream;
let screenStream;
let peers = {};
let peerConnections = {};
const videoContainer = document.getElementById('videoContainer');
// const usersList = document.getElementById('usersList');

// Enhanced STUN/TURN configuration for WebRTC with UDP preference
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' },
        // Add TURN servers when available - important for NAT traversal
        // {
        //     urls: 'turn:your-turn-server.com:3478',
        //     username: 'username',
        //     credential: 'password'
        // }
    ],
    iceTransportPolicy: 'all',
    iceCandidatePoolSize: 10,
    // Explicitly prefer UDP
    rtcpMuxPolicy: 'require',
    bundlePolicy: 'max-bundle'
};
 //thumbnail
 function getQueryParam(name) {
const urlParams = new URLSearchParams(window.location.search);
return urlParams.get(name);
}

// Get username and meeting link from URL parameters
const username = getQueryParam('username') || 'Guest';
const room = getQueryParam('link');

if (!room) {
alert("Meeting link is missing!");
} else {
console.log(`Username: ${username}, Room: ${room}`);

const usersList = document.getElementById('usersList');

// Function to generate a user list item (Google Meet style)
function createUserListItem(user) {
    let initials = "U"; // Default Initials: 'U' for 'User'

    if (user.name && user.name.trim() !== "") {
        initials = user.name.charAt(0).toUpperCase(); // Take First Letter
    }

    // Create list item container
    const li = document.createElement('li');
    li.style.display = "flex";
    li.style.alignItems = "center";
    li.style.gap = "7px";
    li.style.padding = "10px";
    li.style.borderRadius = "18px";
    li.style.background = "rgba(255, 255, 255, 0.05)"; // Slight Transparency
    li.style.marginBottom = "0px";
    li.style.listStyle = "none"; // 🔥 Removes the bullet points!

    // Thumbnail (Circular Avatar)
    const thumbnail = document.createElement('div');
    thumbnail.style.width = "35px";
    thumbnail.style.height = "35px";
    thumbnail.style.display = "flex";
    thumbnail.style.alignItems = "center";
    thumbnail.style.justifyContent = "center";
    thumbnail.style.borderRadius = "50%";
    thumbnail.style.backgroundColor = "#4285F4"; // Google Meet Blue
    thumbnail.style.color = "white";
    thumbnail.style.fontWeight = "bold";
    thumbnail.style.fontSize = "20px";
    thumbnail.style.flexShrink = "0"; // Prevent Shrinking
    thumbnail.textContent = initials;

    // Name container
    const nameContainer = document.createElement('div');
    nameContainer.style.display = "flex";
    nameContainer.style.flexDirection = "column";
    nameContainer.style.gap = "0px";

    // Full name display
    const nameSpan = document.createElement('span');
    nameSpan.style.color = "black";
    nameSpan.style.fontSize = "18px";
    nameSpan.style.fontWeight = "600"; // 🔥 Make it BOLD and Readable
    nameSpan.textContent = user.name;

    // Append elements properly
    nameContainer.appendChild(nameSpan);
    li.appendChild(thumbnail);
    li.appendChild(nameContainer);
    return li;
}

// Function to fetch active users
function fetchActiveUsers() {
    fetch(`/api/active_users/?meeting_link=${encodeURIComponent(room)}`)
        .then(response => response.json())
        .then(data => {
            if (!data.users || !Array.isArray(data.users)) {
                console.error("Invalid API response:", data);
                return;
            }
            usersList.innerHTML = ''; // Clear previous list
            data.users.forEach(user => {
                usersList.appendChild(createUserListItem(user));
            });
        })
        .catch(error => console.error("Error fetching users:", error));
}

// Fetch users on page load
fetchActiveUsers();

// WebSocket connection for real-time updates
const socket = new WebSocket(`ws://localhost:8000/ws/meeting?meeting_link=${encodeURIComponent(room)}`);

socket.onopen = function () {
    console.log("Connected to WebSocket");
};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === 'user_list') {
        usersList.innerHTML = ''; // Clear previous list
        data.users.forEach(user => {
            usersList.appendChild(createUserListItem(user));
        });
    }
};

socket.onerror = function (error) {
    console.error("WebSocket error:", error);
};

socket.onclose = function () {
    console.log("WebSocket connection closed");
};
}


let mediaRecorder;
let recordedChunks = [];

// Start Recording
async function startRecording(roomId, username) {
try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById("video").srcObject = stream; // Show in video element

    mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm; codecs=vp9" });

    mediaRecorder.ondataavailable = function (event) {
        if (event.data.size > 0) {
            // Send each chunk to the server
            socket.emit("record_chunk", {
                room: roomId,
                username: username,
                chunk: event.data
            });
        }
    };

    mediaRecorder.start(1000); // Record in 1-second intervals
} catch (error) {
    console.error("Error accessing media devices:", error);
}
}

// Stop Recording
function stopRecording() {
if (mediaRecorder) {
    mediaRecorder.stop();
    socket.emit("stop_recording", { room: "roomId" });
}
}



// Set advanced audio constraints for better quality
const mediaConstraints = {
    video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 }
    },
    audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        latency: 0.01,
        sampleRate: 48000,
        channelCount: 1,
        volume: 1.0
    }
};

async function initializeMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
        addVideoStream('local', localStream, username);
    } catch (err) {
        console.error('Failed to get media devices:', err);
        
        // Try fallback to only audio if video fails
        try {
            console.log('Attempting to connect with audio only...');
            localStream = await navigator.mediaDevices.getUserMedia({
                video: false,
                audio: true
            });
            addVideoStream('local', localStream, username + ' (audio only)');
        } catch (audioErr) {
            console.error('Failed to get any media devices:', audioErr);
            alert('Please enable camera and/or microphone access');
        }
    }
}

function addVideoStream(userId, stream, username) {
    const wrapper = document.createElement('div');
    wrapper.className = 'video-wrapper';
    wrapper.id = `video-${userId}`;

    const video = document.createElement('video');
    video.srcObject = stream;
    video.autoplay = true;
    video.playsInline = true;
    if (userId === 'local') video.muted = true;

    const label = document.createElement('div');
    label.className = 'username-label';
    label.textContent = username;

    // Add audio level meter
    const audioMeter = document.createElement('div');
    audioMeter.className = 'audio-meter';
    
    wrapper.appendChild(video);
    wrapper.appendChild(label);
    wrapper.appendChild(audioMeter);
    videoContainer.appendChild(wrapper);

    // Set up audio level monitoring
    if (stream.getAudioTracks().length > 0) {
        setupAudioMeter(stream, audioMeter);
    }
}

// Function to monitor audio levels
function setupAudioMeter(stream, meterElement) {
    if (!window.AudioContext) return;
    
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const microphone = audioContext.createMediaStreamSource(stream);
    const javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);
    
    analyser.smoothingTimeConstant = 0.8;
    analyser.fftSize = 1024;
    
    microphone.connect(analyser);
    analyser.connect(javascriptNode);
    javascriptNode.connect(audioContext.destination);
    
    javascriptNode.onaudioprocess = function() {
        const array = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(array);
        const values = array.reduce((a, b) => a + b) / array.length;
        
        // Convert values to a width percentage
        const percent = Math.min(Math.max(0, values / 128 * 100), 100);
        meterElement.style.width = percent + '%';
        
        // Change color based on level
        if (percent > 60) {
            meterElement.style.backgroundColor = '#ff4d4d';
        } else if (percent > 20) {
            meterElement.style.backgroundColor = '#2196F3';
        } else {
            meterElement.style.backgroundColor = '#4CAF50';
        }
    };
}

// Function to set bitrates in SDP for better audio quality with UDP
function setMediaBitrates(sdp) {
    // Set audio bitrate to 128kbps for better quality
    sdp = sdp.replace(/a=mid:audio\r\n/g, 'a=mid:audio\r\nb=AS:128\r\n');
    
    // Set video bitrate to a reasonable value for UDP
    sdp = sdp.replace(/a=mid:video\r\n/g, 'a=mid:video\r\nb=AS:1000\r\n');
    
    // Prioritize UDP transport
    sdp = sdp.replace(/a=candidate:.*tcp.*\r\n/g, '');
    
    return sdp;
}

// Function to filter out TCP candidates to prioritize UDP
function filterIceCandidates(candidate) {
    // Only relay TCP candidates if absolutely needed
    if (candidate.candidate.indexOf('tcp') !== -1) {
        if (candidate.candidate.indexOf('typ relay') !== -1) {
            // Allow relay TCP candidates only
            return true;
        }
        return false;
    }
    return true;
}

async function createPeerConnection(userId, username) {
    const peerConnection = new RTCPeerConnection(configuration);
    peerConnections[userId] = peerConnection;

    // Add local tracks to peer connection
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    // Prioritize audio traffic
    if (peerConnection.getTransceivers) {
        peerConnection.getTransceivers().forEach(transceiver => {
            if (transceiver.sender && transceiver.sender.track) {
                if (transceiver.sender.track.kind === 'audio') {
                    transceiver.direction = 'sendrecv';
                    if (transceiver.setCodecPreferences && RTCRtpSender.getCapabilities) {
                        const codecs = RTCRtpSender.getCapabilities('audio').codecs;
                        // Prefer Opus codec for better audio quality
                        const opusCodecs = codecs.filter(codec => codec.mimeType.toLowerCase() === 'audio/opus');
                        if (opusCodecs.length > 0) {
                            transceiver.setCodecPreferences(opusCodecs);
                        }
                    }
                } else if (transceiver.sender.track.kind === 'video') {
                    // For video, prefer VP8 for better compatibility with UDP
                    if (transceiver.setCodecPreferences && RTCRtpSender.getCapabilities) {
                        const codecs = RTCRtpSender.getCapabilities('video').codecs;
                        const preferredCodecs = codecs.filter(codec => 
                            codec.mimeType.toLowerCase() === 'video/vp8');
                        if (preferredCodecs.length > 0) {
                            transceiver.setCodecPreferences(preferredCodecs);
                        }
                    }
                }
            }
        });
    }

    // Handle incoming tracks
    peerConnection.ontrack = (event) => {
        if (!document.getElementById(`video-${userId}`)) {
            addVideoStream(userId, event.streams[0], username);
        }
    };

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate && filterIceCandidates(event.candidate)) {
            console.log("Sending ICE candidate:", event.candidate.candidate.substr(0, 50) + "...");
            socket.emit('ice_candidate', {
                candidate: event.candidate,
                to: userId,
                room: room
            });
        }
    };

    // Log ICE gathering state changes
    peerConnection.onicegatheringstatechange = () => {
        console.log(`ICE gathering state with ${username}: ${peerConnection.iceGatheringState}`);
    };

    // Monitor connection state for issues
    peerConnection.onconnectionstatechange = () => {
        console.log(`Connection state with ${username}: ${peerConnection.connectionState}`);
        if (peerConnection.connectionState === 'failed' || peerConnection.connectionState === 'disconnected') {
            console.warn(`Connection with ${username} is ${peerConnection.connectionState}. Attempting to reconnect...`);
            // Add delay before reconnect to avoid rapid reconnection attempts
            setTimeout(() => {
                if (peerConnections[userId] && 
                    (peerConnections[userId].connectionState === 'failed' || 
                    peerConnections[userId].connectionState === 'disconnected')) {
                    restartIce(userId);
                }
            }, 2000);
        }
    };

    // Monitor ICE connection state
    peerConnection.oniceconnectionstatechange = () => {
        console.log(`ICE connection state with ${username}: ${peerConnection.iceConnectionState}`);
        if (peerConnection.iceConnectionState === 'failed') {
            console.warn(`ICE connection with ${username} failed. Attempting ICE restart...`);
            restartIce(userId);
        } else if (peerConnection.iceConnectionState === 'disconnected') {
            console.warn(`ICE disconnected with ${username}. Monitoring...`);
            // Give it a chance to recover before forcing a restart
            setTimeout(() => {
                if (peerConnections[userId] && peerConnections[userId].iceConnectionState === 'disconnected') {
                    restartIce(userId);
                }
            }, 3000);
        }
    };

    return peerConnection;
}

// Function to restart ICE if connection fails
async function restartIce(userId) {
    const peerConnection = peerConnections[userId];
    if (peerConnection) {
        try {
            console.log(`Restarting ICE connection with ${userId}`);
            // Create offer with ICE restart
            const offer = await peerConnection.createOffer({ iceRestart: true });
            offer.sdp = setMediaBitrates(offer.sdp);
            await peerConnection.setLocalDescription(offer);
            socket.emit('offer', {
                offer: offer,
                to: userId,
                room: room
            });
        } catch (err) {
            console.error('Error restarting ICE:', err);
        }
    }
}

// Connection monitoring function for quality 
function startConnectionMonitoring(userId) {
    const peerConnection = peerConnections[userId];
    if (!peerConnection) return;
    
    const statsInterval = setInterval(async () => {
        if (!peerConnections[userId]) {
            clearInterval(statsInterval);
            return;
        }
        
        try {
            const stats = await peerConnection.getStats();
            let audioPacketsLost = 0;
            let audioPacketsSent = 0;
            let audioPacketsReceived = 0;
            let audioJitter = 0;
            let audioLevel = 0;
            let videoPacketsLost = 0;
            let videoFrameRate = 0;
            
            stats.forEach(report => {
                if (report.type === 'inbound-rtp' && report.kind === 'audio') {
                    audioPacketsLost = report.packetsLost || 0;
                    audioPacketsReceived = report.packetsReceived || 0;
                    audioJitter = report.jitter || 0;
                    
                    // Calculate packet loss percentage
                    const lossPercentage = audioPacketsReceived > 0 ? 
                        (audioPacketsLost / (audioPacketsLost + audioPacketsReceived) * 100).toFixed(1) : 0;
                    
                    // Log significant packet loss
                    if (lossPercentage > 5) {
                        console.warn(`High audio packet loss with ${userId}: ${lossPercentage}%`);
                    }
                    
                    // Log high jitter
                    if (report.jitter > 0.05) {
                        console.warn(`High audio jitter with ${userId}: ${report.jitter.toFixed(3)} seconds`);
                    }
                }
                
                if (report.type === 'inbound-rtp' && report.kind === 'video') {
                    videoPacketsLost = report.packetsLost || 0;
                    videoFrameRate = report.framesPerSecond || 0;
                    
                    // Log low frame rate
                    if (videoFrameRate < 15 && videoFrameRate > 0) {
                        console.warn(`Low video frame rate with ${userId}: ${videoFrameRate.toFixed(1)} fps`);
                    }
                }
                
                if (report.type === 'media-source' && report.kind === 'audio') {
                    audioLevel = report.audioLevel || 0;
                }
            });
            
            // Only log if there are issues to report
            const audioLoss = audioPacketsReceived > 0 ? 
                (audioPacketsLost / (audioPacketsLost + audioPacketsReceived) * 100).toFixed(1) : 0;
                
            if (audioPacketsLost > 5 || audioJitter > 0.03 || videoFrameRate < 15) {
                console.info(`Connection with ${userId} - Audio loss: ${audioLoss}%, Jitter: ${(audioJitter * 1000).toFixed(1)}ms, Video: ${videoFrameRate.toFixed(1)} fps`);
            }
        } catch (err) {
            console.error('Error getting connection stats:', err);
        }
    }, 5000); // Check every 5 seconds
    
    return statsInterval;
}

// UDP-optimized SDP modifications
function optimizeSdpForUdp(sdp) {
    // Set DSCP values for QoS (if supported by network)
    sdp = sdp.replace(/a=mid:audio\r\n/g, 'a=mid:audio\r\na=rtpmap:111 opus/48000/2\r\na=rtcp-fb:111 nack\r\na=fmtp:111 minptime=10;useinbandfec=1\r\n');
    
    // Add FEC (Forward Error Correction) to video for more resilience over UDP
    sdp = sdp.replace(/a=mid:video\r\n/g, 'a=mid:video\r\na=rtcp-fb:* nack\r\na=rtcp-fb:* nack pli\r\na=rtcp-fb:* ccm fir\r\n');
    
    return sdp;
}

// Socket.IO event handlers
socket.on('connect', async () => {
    console.log('Connected to signaling server');
    await initializeMedia();
    socket.emit('join_room', { room, username });
});

socket.on('connect_error', (err) => {
    console.error('Connection error:', err);
    alert(`Failed to connect to server: ${err.message}`);
});

socket.on('user_joined', async (data) => {
    const { sid: userId, username: peerUsername } = data;
    console.log('User joined:', peerUsername);

    // Create peer connection for new user
    const peerConnection = await createPeerConnection(userId, peerUsername);
    startConnectionMonitoring(userId);

    // Create and send offer
    try {
        const offer = await peerConnection.createOffer();
        // Improve audio quality by modifying SDP
        offer.sdp = setMediaBitrates(offer.sdp);
        offer.sdp = optimizeSdpForUdp(offer.sdp);
        await peerConnection.setLocalDescription(offer);
        
        console.log('Sending offer to', peerUsername);
        socket.emit('offer', {
            offer: offer,
            to: userId,
            room: room
        });
    } catch (err) {
        console.error('Error creating offer:', err);
    }
});

socket.on('offer', async (data) => {
    const { from: userId, offer, username: peerUsername } = data;
    console.log('Received offer from:', peerUsername);
    
    try {
        // Create peer connection if it doesn't exist
        if (!peerConnections[userId]) {
            await createPeerConnection(userId, peerUsername);
            startConnectionMonitoring(userId);
        }
        
        const peerConnection = peerConnections[userId];
        
        // Set the remote description using incoming offer
        await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
        
        // Create answer
        const answer = await peerConnection.createAnswer();
        // Improve audio quality by modifying SDP
        answer.sdp = setMediaBitrates(answer.sdp);
        answer.sdp = optimizeSdpForUdp(answer.sdp);
        await peerConnection.setLocalDescription(answer);
        
        console.log('Sending answer to', peerUsername);
        socket.emit('answer', {
            answer: answer,
            to: userId,
            room: room
        });
    } catch (err) {
        console.error('Error handling offer:', err);
    }
});

socket.on('answer', async (data) => {
    const { from: userId, answer } = data;
    const peerConnection = peerConnections[userId];
    if (peerConnection) {
        try {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            console.log('Connection established with remote peer');
        } catch (err) {
            console.error('Error setting remote description from answer:', err);
        }
    }
});

socket.on('ice_candidate', async (data) => {
    const { from: userId, candidate } = data;
    const peerConnection = peerConnections[userId];
    if (peerConnection) {
        try {
            const iceCandidate = new RTCIceCandidate(candidate);
            
            // Check if this is a UDP candidate
            if (iceCandidate.candidate.indexOf('udp') !== -1 || 
                iceCandidate.candidate.indexOf('typ relay') !== -1) {
                console.log(`Adding ICE candidate from ${userId}: ${iceCandidate.candidate.substr(0, 50)}...`);
                await peerConnection.addIceCandidate(iceCandidate);
            } else {
                console.log(`Skipping non-UDP ICE candidate: ${iceCandidate.candidate.substr(0, 50)}...`);
                // Still add TCP candidates as a fallback if we don't have many UDP candidates
                if (peerConnection.iceGatheringState === 'complete') {
                    await peerConnection.addIceCandidate(iceCandidate);
                }
            }
        } catch (err) {
            console.error('Error adding ICE candidate:', err);
        }
    }
});




// socket.on('user_list', (users) => {
//     usersList.innerHTML = '';
//     users.forEach(user => {
//         const li = document.createElement('li');
//         li.textContent = user.username;
//         usersList.appendChild(li);
//     });
// });

socket.on('user_disconnected', (userId) => {
    const videoElement = document.getElementById(`video-${userId}`);
    if (videoElement) {
        videoElement.remove();
    }
    if (peerConnections[userId]) {
        peerConnections[userId].close();
        delete peerConnections[userId];
    }
});

// Network connectivity test
async function testNetworkConnectivity() {
    const testPc = new RTCPeerConnection(configuration);
    let candidatesFound = false;
    
    return new Promise((resolve) => {
        const timeout = setTimeout(() => {
            testPc.close();
            resolve({
                status: candidatesFound ? 'limited' : 'failed',
                message: candidatesFound ? 
                    'Limited connectivity detected. You may experience issues.' : 
                    'No connectivity detected. Please check your network settings.'
            });
        }, 5000);
        
        testPc.onicecandidate = (e) => {
            if (e.candidate) {
                candidatesFound = true;
                // Check if we found non-host candidates which indicate good connectivity
                if (e.candidate.candidate.indexOf('typ srflx') !== -1 || 
                    e.candidate.candidate.indexOf('typ relay') !== -1) {
                    clearTimeout(timeout);
                    testPc.close();
                    resolve({
                        status: 'good',
                        message: 'Network connectivity looks good.'
                    });
                }
            }
        };
        
        testPc.onicegatheringstatechange = () => {
            if (testPc.iceGatheringState === 'complete') {
                clearTimeout(timeout);
                testPc.close();
                resolve({
                    status: candidatesFound ? 'limited' : 'failed',
                    message: candidatesFound ? 
                        'Limited connectivity detected. You may experience issues.' : 
                        'No connectivity detected. Please check your network settings.'
                });
            }
        };
        
        // Create data channel to trigger ICE gathering
        testPc.createDataChannel('connectivity-test');
        testPc.createOffer()
            .then(offer => testPc.setLocalDescription(offer))
            .catch(err => {
                console.error('Error in connectivity test:', err);
                clearTimeout(timeout);
                testPc.close();
                resolve({
                    status: 'error',
                    message: 'Error testing network: ' + err.message
                });
            });
    });
}

// Run network test on startup
window.addEventListener('load', async () => {
    const connectivityResult = await testNetworkConnectivity();
    if (connectivityResult.status !== 'good') {
        console.warn('Network connectivity issue:', connectivityResult.message);
        const warningDiv = document.createElement('div');
        warningDiv.className = 'network-warning';
        warningDiv.textContent = connectivityResult.message;
        document.body.insertBefore(warningDiv, document.body.firstChild);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            warningDiv.style.opacity = '0';
            setTimeout(() => warningDiv.remove(), 1000);
        }, 10000);
    }
});

// Control button handlers
document.getElementById('videoBtn').onclick = () => {
    const videoTrack = localStream.getVideoTracks()[0];
    if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        document.getElementById('videoBtn').classList.toggle('active');
    }
};

document.getElementById('audioBtn').onclick = () => {
    const audioTrack = localStream.getAudioTracks()[0];
    if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        document.getElementById('audioBtn').classList.toggle('active');
    }
};

document.getElementById('screenBtn').onclick = async () => {
    if (!screenStream) {
        try {
            screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: "always",
                    frameRate: { ideal: 15 } // Lower framerate for screen share to save bandwidth
                },
                audio: false
            });
            const videoTrack = screenStream.getVideoTracks()[0];
            
            // Replace video track in all peer connections
            Object.values(peerConnections).forEach(pc => {
                const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
                if (sender) sender.replaceTrack(videoTrack);
            });
            
            // Replace local video
            const localVideo = document.querySelector('#video-local video');
            const oldStream = localVideo.srcObject;
            const newStream = new MediaStream([
                videoTrack,
                ...oldStream.getAudioTracks()
            ]);
            localVideo.srcObject = newStream;
            
            videoTrack.onended = stopScreenShare;
            document.getElementById('screenBtn').classList.add('active');
        } catch (err) {
            console.error('Failed to share screen:', err);
        }
    } else {
        stopScreenShare();
    }
};

function stopScreenShare() {
    if (screenStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        
        // Replace screen share with camera in all peer connections
        Object.values(peerConnections).forEach(pc => {
            const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
            if (sender && videoTrack) sender.replaceTrack(videoTrack);
        });
        
        // Replace local video
        const localVideo = document.querySelector('#video-local video');
        localVideo.srcObject = localStream;
        
        screenStream.getTracks().forEach(track => track.stop());
        screenStream = null;
        document.getElementById('screenBtn').classList.remove('active');
    }
}

document.getElementById('leaveBtn').onclick = () => {
    socket.emit('leave_room', { room });
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    if (screenStream) {
        screenStream.getTracks().forEach(track => track.stop());
    }
    Object.values(peerConnections).forEach(pc => pc.close());
    window.location.href = '/';
};

// Network quality indicator
function updateNetworkQualityIndicator() {
    // Add a network quality indicator to the UI
    const indicator = document.createElement('div');
    indicator.id = 'network-quality';
    indicator.className = 'network-quality good';
    indicator.innerHTML = '<span></span>';
    document.body.appendChild(indicator);
    
    // Update it periodically
    setInterval(async () => {
        let totalPacketLoss = 0;
        let totalPackets = 0;
        let maxJitter = 0;
        let connectionCount = 0;
        
        for (const pcId in peerConnections) {
            try {
                const stats = await peerConnections[pcId].getStats();
                stats.forEach(report => {
                    if (report.type === 'inbound-rtp') {
                        totalPacketLoss += report.packetsLost || 0;
                        totalPackets += report.packetsReceived || 0;
                        maxJitter = Math.max(maxJitter, report.jitter || 0);
                        connectionCount++;
                    }
                });
            } catch (e) {
                // Ignore errors in stats gathering
            }
        }
        
        // Calculate packet loss percentage
        const lossPercentage = totalPackets > 0 ? 
            (totalPacketLoss / (totalPacketLoss + totalPackets) * 100) : 0;
            
        // Update the indicator
        indicator.className = 'network-quality';
        if (lossPercentage > 10 || maxJitter > 0.1) {
            indicator.classList.add('bad');
        } else if (lossPercentage > 3 || maxJitter > 0.05) {
            indicator.classList.add('fair');
        } else {
            indicator.classList.add('good');
        }
    }, 3000);
}

// Call network quality indicator on start
window.addEventListener('load', updateNetworkQualityIndicator);

// Handle window close/refresh
window.onbeforeunload = () => {
    socket.emit('leave_room', { room });
};