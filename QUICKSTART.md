# Quick Start Guide - Emotion Music Generator

## 🚀 Fastest Setup (3 steps)

### Option A: Using the run script
```bash
# 1. Clone the repository
git clone <repository-url>
cd emotion-music-generator

# 2. Make script executable
chmod +x run.sh

# 3. Run the application
./run.sh
```

### Option B: Using Docker
```bash
# 1. Clone the repository
git clone <repository-url>
cd emotion-music-generator

# 2. Run with Docker
./run.sh docker
```

### Option C: Manual setup
```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open browser
# Navigate to http://localhost:8000
```

## 🎯 First Use

1. **Allow Camera Access** - Click "Allow" when browser asks for camera permission
2. **Click "Start Detection"** - Begin emotion detection
3. **Make Different Expressions** - Try smiling, frowning, looking surprised
4. **Listen to Music Changes** - Notice how music adapts to your emotions
5. **Adjust Controls** - Try changing volume, style, or manual override

## 🔧 Troubleshooting

### Camera not working?
- Check browser permissions (Settings → Privacy → Camera)
- Try Chrome or Firefox
- Ensure no other app is using camera

### No sound?
- Check system volume
- Ensure browser tab is not muted
- Try refreshing the page

### Low performance?
- Close other applications
- Use Chrome for best performance
- Reduce browser tabs

## 📱 Mobile Support

The app works on mobile devices with front-facing cameras:
1. Open in mobile browser
2. Allow camera access
3. Use in landscape mode for best experience

## 🎨 Emotion Colors

- 😊 Happy - Gold
- 😢 Sad - Blue  
- 😠 Angry - Red
- 😲 Surprise - Purple
- 😐 Neutral - Gray
- 😨 Fear - Orange
- 🤢 Disgust - Green

## 💡 Tips

- **Best Lighting**: Use good lighting for accurate detection
- **Face Position**: Keep face centered in frame
- **Multiple People**: System averages emotions from all faces
- **Calibration**: Use calibrate button to improve accuracy

## 🆘 Need Help?

- Check full README.md for detailed documentation
- View logs in `backend/emotion_music.log`
- Open browser console for frontend errors
- Create GitHub issue for bugs

Enjoy your emotion-driven music experience! 🎵✨