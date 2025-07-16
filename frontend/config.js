// Frontend configuration for different environments
const config = {
    development: {
        API_URL: 'http://localhost:8000',
        WS_URL: 'ws://localhost:8000/ws'
    },
    production: {
        // These will be replaced with your actual deployed backend URLs
        API_URL: process.env.REACT_APP_API_URL || 'https://emotion-music-api.onrender.com',
        WS_URL: process.env.REACT_APP_WS_URL || 'wss://emotion-music-api.onrender.com/ws'
    }
};

// Determine environment
const environment = window.location.hostname === 'localhost' ? 'development' : 'production';

// Export configuration
window.APP_CONFIG = config[environment];