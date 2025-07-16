# 🚀 Deploy Your Emotion AI App - Step by Step

This guide will help you deploy your app for FREE in about 10-15 minutes.

## 📋 What You'll Get:
- Frontend hosted on Vercel (instant, global CDN)
- Backend API on Render (free tier)
- Fully functional emotion detection app
- HTTPS enabled (required for camera)

---

## Step 1: Deploy Frontend to Vercel (5 minutes)

### Option A: Using Vercel Website (Easiest)

1. **Go to Vercel Import**: https://vercel.com/import/git

2. **Click "Import Third-Party Git Repository"**
   - Enter: `https://github.com/ProPrak01/emotion-ai`

3. **Configure your project**:
   - Project Name: `emotion-ai` (or any name you like)
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: ` ` (leave empty)
   - Output Directory: `frontend`
   - Install Command: ` ` (leave empty)

4. **Add Environment Variable** (IMPORTANT):
   - Click "Add"
   - Name: `VITE_API_URL`
   - Value: `https://emotion-ai-api.onrender.com` (we'll update this later)

5. **Click "Deploy"**

6. **Save your URL**: Your frontend will be at something like:
   - `https://emotion-ai-xxxxx.vercel.app`

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts:
# - Set up and deploy: Y
# - Which scope: (select your account)
# - Link to existing project: N
# - Project name: emotion-ai
# - Directory: ./
# - Override settings: Y
# - Output directory: frontend
```

---

## Step 2: Deploy Backend to Render (10 minutes)

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub**:
   - Click "Connect GitHub"
   - Authorize Render
   - Select repository: `ProPrak01/emotion-ai`

4. **Configure your service**:
   - Name: `emotion-ai-api`
   - Environment: `Python`
   - Region: Choose closest to you
   - Branch: `main`
   - Root Directory: ` ` (leave empty)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app_lite:app --host 0.0.0.0 --port $PORT`

5. **Choose Instance Type**: 
   - Select **"Free"** ($0/month)

6. **Add Environment Variables**:
   Click "Advanced" and add:
   - `FRONTEND_URL` = (your Vercel URL from Step 1, e.g., `https://emotion-ai-xxxxx.vercel.app`)
   - `PYTHON_VERSION` = `3.9`

7. **Click "Create Web Service"**

8. **Wait for deployment** (5-10 minutes)
   - Render will build and deploy your backend
   - Copy the URL when done (e.g., `https://emotion-ai-api.onrender.com`)

---

## Step 3: Connect Frontend to Backend

1. **Go back to Vercel Dashboard**: https://vercel.com/dashboard

2. **Click on your project** → **Settings** → **Environment Variables**

3. **Update the API URL**:
   - Edit `VITE_API_URL`
   - New value: Your Render URL (e.g., `https://emotion-ai-api.onrender.com`)

4. **Redeploy Frontend**:
   - Go to "Deployments" tab
   - Click "..." on latest deployment
   - Click "Redeploy"

---

## Step 4: Test Your App! 🎉

1. **Open your Vercel URL** in a browser
2. **Allow camera permissions** when prompted
3. **Click "Start Detection"**
4. **Make different facial expressions**
5. **Watch the music adapt to your emotions!**

---

## 🔧 Troubleshooting

### Backend takes long to respond?
- Render free tier sleeps after 15 mins
- First request takes ~30 seconds to wake up
- Solution: Visit your backend URL directly first: `https://emotion-ai-api.onrender.com/health`

### Camera not working?
- Make sure you're using HTTPS (Vercel provides this)
- Try Chrome or Firefox
- Check browser permissions

### CORS errors?
- Make sure `FRONTEND_URL` in Render matches your Vercel URL exactly
- Include `https://` in the URL

---

## 📊 Free Tier Limits

### Vercel (Frontend)
- ✅ 100GB bandwidth/month (plenty!)
- ✅ Unlimited deployments
- ✅ Auto HTTPS
- ✅ Global CDN

### Render (Backend)
- ✅ 750 hours/month (covers 24/7)
- ⚠️ Sleeps after 15 mins inactivity
- ⚠️ 512MB RAM (using optimized `app_lite.py`)

---

## 🎯 Next Steps

1. **Share your app!** 
   - Your app URL: `https://emotion-ai-xxxxx.vercel.app`

2. **Keep backend awake** (optional):
   - Use https://uptimerobot.com (free)
   - Monitor your Render URL every 10 minutes

3. **Custom domain** (optional):
   - Both Vercel and Render support custom domains

---

## 🆘 Need Help?

- Vercel deployment issues: Check build logs in Vercel dashboard
- Render deployment issues: Check logs in Render dashboard
- App not working: Check browser console (F12)

Your app should now be live! Share the URL and let people experience emotion-driven music! 🎵😊