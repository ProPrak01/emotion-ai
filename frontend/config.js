// Frontend configuration for different environments
const config = {
    development: {
        API_URL: 'http://localhost:8000',
        WS_URL: 'ws://localhost:8000/ws'
    },
    production: {
        // Update these URLs after deploying your backend
        API_URL: 'https://emotion-ai-api.onrender.com',
        WS_URL: 'wss://emotion-ai-api.onrender.com/ws'
    }
};

// Determine environment
const environment = window.location.hostname === 'localhost' ? 'development' : 'production';

// Export configuration
window.APP_CONFIG = config[environment];