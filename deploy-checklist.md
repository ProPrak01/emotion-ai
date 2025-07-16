# ✅ Deployment Checklist

## Frontend (Vercel)
- [ ] Go to https://vercel.com/import/git
- [ ] Import: https://github.com/ProPrak01/emotion-ai
- [ ] Set root directory: `./`
- [ ] Set output directory: `frontend`
- [ ] Add env variable: `VITE_API_URL=https://emotion-ai-api.onrender.com`
- [ ] Deploy and copy URL: _________________________

## Backend (Render)
- [ ] Go to https://dashboard.render.com/
- [ ] Create new Web Service
- [ ] Connect GitHub: ProPrak01/emotion-ai
- [ ] Name: emotion-ai-api
- [ ] Build: `pip install -r requirements.txt`
- [ ] Start: `cd backend && uvicorn app_lite:app --host 0.0.0.0 --port $PORT`
- [ ] Choose FREE tier
- [ ] Add env: `FRONTEND_URL=` (your Vercel URL)
- [ ] Deploy and copy URL: _________________________

## Final Steps
- [ ] Update Vercel env variable with Render URL
- [ ] Redeploy Vercel
- [ ] Test camera access
- [ ] Test emotion detection
- [ ] Share your app! 🎉

## Your URLs:
- Frontend: _________________________
- Backend: _________________________
- GitHub: https://github.com/ProPrak01/emotion-ai