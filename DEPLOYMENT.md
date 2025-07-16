# 🚀 Deployment Guide - Emotion Music Generator

This guide covers deploying the application using **FREE** hosting providers.

## 📋 Prerequisites

1. GitHub account (for code hosting)
2. Accounts on deployment platforms (all free):
   - [Vercel](https://vercel.com) - Frontend hosting
   - [Render](https://render.com) - Backend hosting
   - [Replit](https://replit.com) - Alternative all-in-one option

## 🎯 Deployment Strategy

- **Frontend**: Vercel/Netlify (static hosting)
- **Backend**: Render/Railway (Python app hosting)
- **Alternative**: Replit (full-stack hosting)

## 📦 Step 1: Prepare Your Code

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/emotion-music-generator.git
   git push -u origin main
   ```

## 🎨 Step 2: Deploy Frontend (Vercel)

1. **Go to [Vercel](https://vercel.com)**
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: `echo "No build needed"`
   - Output Directory: `frontend`
5. Add Environment Variable:
   - `VITE_API_URL` = Your Render backend URL (will add after backend deployment)
6. Click "Deploy"

### Alternative: Netlify

1. **Go to [Netlify](https://netlify.com)**
2. Drag and drop the `frontend` folder
3. Update `frontend/config.js` with your backend URL

## 🔧 Step 3: Deploy Backend (Render)

1. **Go to [Render](https://render.com)**
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: `emotion-music-api`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Choose **Free** plan
6. Add Environment Variables:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   DEBUG=false
   PYTHON_VERSION=3.9
   ```
7. Click "Create Web Service"

### Important: Update Frontend

After backend deployment:
1. Copy your Render URL (e.g., `https://emotion-music-api.onrender.com`)
2. Go back to Vercel
3. Settings → Environment Variables
4. Update `VITE_API_URL` with your Render URL
5. Redeploy frontend

## 🎯 Step 4: Alternative - Deploy on Replit

For a simpler all-in-one deployment:

1. **Go to [Replit](https://replit.com)**
2. Click "Create Repl"
3. Import from GitHub
4. Select your repository
5. Replit will auto-detect Python
6. Click "Run" to start

### Replit Configuration
The `.replit` and `replit.nix` files are already configured for:
- Python 3.9 environment
- Required system dependencies
- Auto-start on port 8000
- OpenCV and TensorFlow support

## 🔐 Environment Variables

### Backend (Render/Railway):
```env
# Required
FRONTEND_URL=https://your-frontend.vercel.app
DEBUG=false

# Optional (defaults are fine)
EMOTION_DETECTION_MODEL=fer
CONFIDENCE_THRESHOLD=0.5
EMOTION_SMOOTHING_FRAMES=5
MAX_FACES=5
DETECTION_FPS=15
```

### Frontend (Vercel):
```env
VITE_API_URL=https://your-backend.onrender.com
```

## 🚨 Common Issues & Solutions

### 1. CORS Errors
- Ensure `FRONTEND_URL` is set correctly in backend
- Check that frontend is using HTTPS

### 2. Slow Initial Load (Render)
- Free tier goes to sleep after 15 mins
- First request takes ~30 seconds to wake up
- Consider using a service like [UptimeRobot](https://uptimerobot.com) to keep it awake

### 3. Camera Not Working
- HTTPS is required for camera access
- Ensure your deployment uses HTTPS (Vercel/Netlify do this automatically)

### 4. WebSocket Connection Failed
- Update `frontend/config.js` with correct WebSocket URL
- Use `wss://` instead of `ws://` for HTTPS deployments

## 📊 Free Tier Limits

### Vercel
- ✅ Unlimited websites
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN

### Render
- ✅ 750 hours/month (enough for 24/7)
- ✅ Auto-deploy from GitHub
- ⚠️ Spins down after 15 mins inactivity
- ⚠️ 512MB RAM limit

### Replit
- ✅ Always-on for public repls
- ✅ 1GB RAM, 1GB storage
- ✅ Custom domains (with Hacker plan)
- ⚠️ Limited CPU

## 🎯 Production Checklist

- [ ] GitHub repository created
- [ ] Frontend deployed to Vercel/Netlify
- [ ] Backend deployed to Render/Railway
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] WebSocket URL updated in frontend
- [ ] Camera permissions tested
- [ ] Performance monitored

## 🔗 Useful Links

- [Vercel Docs](https://vercel.com/docs)
- [Render Docs](https://render.com/docs)
- [Replit Docs](https://docs.replit.com)
- [GitHub Actions](https://docs.github.com/en/actions)

## 💡 Tips for Free Hosting

1. **Minimize Dependencies**: Remove unused packages to reduce build time
2. **Optimize Images**: Use WebP format for smaller file sizes
3. **Enable Caching**: Use browser caching for static assets
4. **Monitor Usage**: Keep track of your free tier limits
5. **Use CDNs**: Load libraries from CDNs instead of bundling

## 🚀 Next Steps

After deployment:
1. Test all features thoroughly
2. Set up monitoring (free options: UptimeRobot, Sentry)
3. Optimize performance based on metrics
4. Share your deployed app! 🎉

---

Need help? Create an issue on GitHub or check the troubleshooting section above.