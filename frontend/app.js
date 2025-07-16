// Global variables
let webcamStream = null;
let ws = null;
let isDetecting = false;
let emotionChart = null;
let historyChart = null;
let sessionStartTime = null;
let frameCount = 0;
let lastFrameTime = Date.now();
let emotionHistory = [];
let audioContext = null;
let analyser = null;
let animationId = null;

// Configuration
const WS_URL = window.APP_CONFIG?.WS_URL || 'ws://localhost:8000/ws';
const API_URL = window.APP_CONFIG?.API_URL || 'http://localhost:8000';
const EMOTION_COLORS = {
    happy: '#FFD700',
    sad: '#4169E1',
    angry: '#DC143C',
    surprise: '#9370DB',
    neutral: '#808080',
    fear: '#FF6347',
    disgust: '#32CD32'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', initialize);

function initialize() {
    setupWebcam();
    setupCharts();
    setupEventListeners();
    setupParticles();
    initializeAudioContext();
}

// Webcam setup
async function setupWebcam() {
    const video = document.getElementById('webcam');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        
        video.srcObject = stream;
        webcamStream = stream;
        
        // Setup overlay canvas
        video.addEventListener('loadedmetadata', () => {
            const canvas = document.getElementById('overlay-canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        });
        
    } catch (error) {
        showMessage('Camera access denied. Please enable camera permissions.', 'error');
        console.error('Webcam setup error:', error);
    }
}

// Chart setup
function setupCharts() {
    // Emotion levels chart
    const emotionCtx = document.getElementById('emotion-chart').getContext('2d');
    emotionChart = new Chart(emotionCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(EMOTION_COLORS),
            datasets: [{
                label: 'Emotion Level',
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: Object.values(EMOTION_COLORS),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        color: '#333'
                    },
                    ticks: {
                        color: '#b0b0b0'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#b0b0b0'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // History chart
    const historyCtx = document.getElementById('history-chart').getContext('2d');
    historyChart = new Chart(historyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: Object.keys(EMOTION_COLORS).map(emotion => ({
                label: emotion,
                data: [],
                borderColor: EMOTION_COLORS[emotion],
                backgroundColor: EMOTION_COLORS[emotion] + '20',
                borderWidth: 2,
                tension: 0.4,
                hidden: emotion !== 'neutral'
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        color: '#333'
                    },
                    ticks: {
                        color: '#b0b0b0'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#b0b0b0',
                        maxTicksLimit: 10
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#b0b0b0'
                    }
                }
            }
        }
    });
}

// Event listeners
function setupEventListeners() {
    // Control buttons
    document.getElementById('start-btn').addEventListener('click', startDetection);
    document.getElementById('stop-btn').addEventListener('click', stopDetection);
    document.getElementById('calibrate-btn').addEventListener('click', calibrate);
    
    // Music controls
    document.getElementById('volume-slider').addEventListener('input', updateVolume);
    document.getElementById('style-select').addEventListener('change', updateStyle);
    document.getElementById('manual-slider').addEventListener('input', updateManualControl);
}

// WebSocket connection
function connectWebSocket() {
    ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        showMessage('Connected to server', 'success');
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        showMessage('Connection error', 'error');
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        if (isDetecting) {
            stopDetection();
        }
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'emotion_result':
            updateEmotionDisplay(message.data);
            break;
        case 'music_update':
            updateMusicDisplay(message.data);
            break;
        case 'emotion_update':
            updateCharts(message.data);
            break;
    }
}

// Start emotion detection
function startDetection() {
    if (!webcamStream) {
        showMessage('Please enable camera first', 'error');
        return;
    }
    
    isDetecting = true;
    sessionStartTime = Date.now();
    
    document.getElementById('start-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;
    
    connectWebSocket();
    
    // Start capturing frames
    captureFrames();
    
    // Update session timer
    updateSessionTime();
}

// Stop emotion detection
function stopDetection() {
    isDetecting = false;
    
    document.getElementById('start-btn').disabled = false;
    document.getElementById('stop-btn').disabled = true;
    
    if (ws) {
        ws.close();
        ws = null;
    }
    
    // Send reset command
    sendControlMessage('reset');
}

// Capture and send frames
function captureFrames() {
    if (!isDetecting) return;
    
    const video = document.getElementById('webcam');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    
    // Draw video frame
    ctx.drawImage(video, 0, 0);
    
    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Send via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'frame',
            data: imageData
        }));
    }
    
    // Update FPS
    frameCount++;
    const now = Date.now();
    if (now - lastFrameTime >= 1000) {
        document.getElementById('fps-counter').textContent = `${frameCount} FPS`;
        frameCount = 0;
        lastFrameTime = now;
    }
    
    // Schedule next frame
    setTimeout(() => captureFrames(), 1000 / 15); // 15 FPS
}

// Update emotion display
function updateEmotionDisplay(data) {
    if (!data.success) return;
    
    // Update dominant emotion
    document.getElementById('dominant-emotion').textContent = data.dominant_emotion;
    document.getElementById('confidence').textContent = `${Math.round(data.confidence * 100)}%`;
    
    // Update body data attribute for styling
    document.body.setAttribute('data-emotion', data.dominant_emotion);
    
    // Draw face boxes on overlay
    if (data.faces && data.faces.length > 0) {
        drawFaceOverlay(data.faces);
    }
    
    // Update charts
    updateCharts(data);
    
    // Update stats
    updateStats(data);
}

// Draw face overlay
function drawFaceOverlay(faces) {
    const canvas = document.getElementById('overlay-canvas');
    const ctx = canvas.getContext('2d');
    const video = document.getElementById('webcam');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    faces.forEach(face => {
        const box = face.box;
        const emotions = face.emotions;
        
        // Draw box
        ctx.strokeStyle = EMOTION_COLORS[getDominantEmotion(emotions)];
        ctx.lineWidth = 3;
        ctx.strokeRect(box[0], box[1], box[2], box[3]);
        
        // Draw emotion label
        const dominant = getDominantEmotion(emotions);
        ctx.fillStyle = ctx.strokeStyle;
        ctx.font = '16px Arial';
        ctx.fillText(dominant, box[0], box[1] - 5);
    });
}

// Get dominant emotion from scores
function getDominantEmotion(emotions) {
    return Object.entries(emotions).reduce((a, b) => a[1] > b[1] ? a : b)[0];
}

// Update charts
function updateCharts(data) {
    if (!data.emotions) return;
    
    // Update emotion levels
    const emotionValues = Object.keys(EMOTION_COLORS).map(emotion => 
        data.emotions[emotion] || 0
    );
    emotionChart.data.datasets[0].data = emotionValues;
    emotionChart.update('none');
    
    // Update history
    const timestamp = new Date().toLocaleTimeString();
    
    if (historyChart.data.labels.length > 30) {
        historyChart.data.labels.shift();
        historyChart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    historyChart.data.labels.push(timestamp);
    historyChart.data.datasets.forEach(dataset => {
        const emotion = dataset.label;
        dataset.data.push(data.emotions[emotion] || 0);
    });
    historyChart.update('none');
    
    // Store in history
    emotionHistory.push({
        timestamp: Date.now(),
        emotions: data.emotions,
        dominant: data.dominant_emotion
    });
}

// Update music display
function updateMusicDisplay(data) {
    document.getElementById('music-emotion').textContent = data.current_emotion;
    document.getElementById('tempo-value').textContent = `${data.params.tempo.toFixed(1)}x`;
    document.getElementById('reverb-value').textContent = `${Math.round(data.params.reverb * 100)}%`;
    document.getElementById('brightness-value').textContent = `${Math.round(data.params.brightness * 100)}%`;
}

// Update statistics
function updateStats(data) {
    // Total detections
    const totalDetections = emotionHistory.length;
    document.getElementById('total-detections').textContent = totalDetections;
    
    // Dominant mood (most common emotion)
    if (emotionHistory.length > 0) {
        const emotionCounts = {};
        emotionHistory.forEach(entry => {
            emotionCounts[entry.dominant] = (emotionCounts[entry.dominant] || 0) + 1;
        });
        const dominantMood = Object.entries(emotionCounts).reduce((a, b) => a[1] > b[1] ? a : b)[0];
        document.getElementById('dominant-mood').textContent = dominantMood;
    }
}

// Update session time
function updateSessionTime() {
    if (!isDetecting || !sessionStartTime) return;
    
    const elapsed = Date.now() - sessionStartTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    document.getElementById('session-time').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    requestAnimationFrame(updateSessionTime);
}

// Control message helpers
function sendControlMessage(action, value = null) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'control',
            action: action,
            value: value
        }));
    }
}

function updateVolume(event) {
    const volume = event.target.value / 100;
    document.getElementById('volume-value').textContent = `${event.target.value}%`;
    sendControlMessage('set_volume', volume);
}

function updateStyle(event) {
    const style = event.target.value;
    sendControlMessage('set_style', style);
}

function updateManualControl(event) {
    const value = event.target.value;
    document.getElementById('manual-value').textContent = `${value}%`;
    // TODO: Implement manual emotion control
}

// Calibration
async function calibrate() {
    showMessage('Calibration feature coming soon!', 'info');
    // TODO: Implement calibration UI
}

// Audio visualization
function initializeAudioContext() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        // Start visualization
        visualizeAudio();
    } catch (error) {
        console.error('Audio context error:', error);
    }
}

function visualizeAudio() {
    const canvas = document.getElementById('audio-visualizer');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    function draw() {
        animationId = requestAnimationFrame(draw);
        
        analyser.getByteFrequencyData(dataArray);
        
        ctx.fillStyle = '#2a2a2a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i] / 2;
            
            const emotion = document.body.getAttribute('data-emotion') || 'neutral';
            ctx.fillStyle = EMOTION_COLORS[emotion];
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }
    
    // Simulate audio data for demo
    if (!audioContext.state || audioContext.state === 'suspended') {
        function simulateAudio() {
            for (let i = 0; i < dataArray.length; i++) {
                dataArray[i] = Math.random() * 128 + Math.sin(Date.now() * 0.001 + i * 0.1) * 64;
            }
        }
        setInterval(simulateAudio, 50);
    }
    
    draw();
}

// Particle effects
function setupParticles() {
    const container = document.getElementById('particles');
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.backgroundColor = Object.values(EMOTION_COLORS)[Math.floor(Math.random() * 7)];
        container.appendChild(particle);
    }
}

// Message display
function showMessage(text, type = 'info') {
    const container = document.getElementById('message-container');
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    container.appendChild(message);
    
    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 300);
    }, 3000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
    }
    if (ws) {
        ws.close();
    }
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
});