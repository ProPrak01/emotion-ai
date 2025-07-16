#!/bin/bash

# Emotion Music Generator - Deployment Helper Script

echo "🚀 Emotion Music Generator - Deployment Helper"
echo "=============================================="

# Function to display menu
show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Deploy Frontend to Vercel"
    echo "2) Deploy Frontend to Netlify"
    echo "3) Prepare Backend for Render"
    echo "4) Prepare for Replit"
    echo "5) Setup GitHub repository"
    echo "6) Update production URLs"
    echo "7) Exit"
}

# Setup GitHub repository
setup_github() {
    echo "📦 Setting up GitHub repository..."
    
    read -p "Enter your GitHub username: " github_username
    read -p "Enter repository name (emotion-music-generator): " repo_name
    repo_name=${repo_name:-emotion-music-generator}
    
    git init
    git add .
    git commit -m "Initial commit: Emotion Music Generator"
    git branch -M main
    git remote add origin "https://github.com/$github_username/$repo_name.git"
    
    echo "✅ GitHub repository configured!"
    echo "📌 Run 'git push -u origin main' to push your code"
}

# Deploy to Vercel
deploy_vercel() {
    echo "🎨 Deploying Frontend to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        echo "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    echo "📌 Make sure you're logged in to Vercel"
    vercel login
    
    echo "🚀 Deploying..."
    vercel --prod
    
    echo "✅ Frontend deployed to Vercel!"
    echo "📌 Don't forget to add environment variables in Vercel dashboard"
}

# Deploy to Netlify
deploy_netlify() {
    echo "🎨 Preparing for Netlify deployment..."
    
    echo "📁 Creating deployment bundle..."
    zip -r netlify-deploy.zip frontend/ netlify.toml
    
    echo "✅ Deployment bundle created: netlify-deploy.zip"
    echo ""
    echo "📌 Next steps:"
    echo "1. Go to https://app.netlify.com"
    echo "2. Drag and drop netlify-deploy.zip"
    echo "3. Update API_URL in frontend/config.js after backend deployment"
}

# Prepare for Render
prepare_render() {
    echo "🔧 Preparing Backend for Render..."
    
    # Use lightweight version for free tier
    cp Procfile.lite Procfile
    
    echo "✅ Backend prepared for Render!"
    echo ""
    echo "📌 Next steps:"
    echo "1. Push code to GitHub"
    echo "2. Go to https://render.com"
    echo "3. Create new Web Service"
    echo "4. Connect GitHub repository"
    echo "5. Use these settings:"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: cd backend && uvicorn app_lite:app --host 0.0.0.0 --port \$PORT"
}

# Prepare for Replit
prepare_replit() {
    echo "🎯 Preparing for Replit deployment..."
    
    echo "✅ Replit configuration files already present!"
    echo ""
    echo "📌 Next steps:"
    echo "1. Go to https://replit.com"
    echo "2. Create new Repl from GitHub"
    echo "3. Import this repository"
    echo "4. Click Run!"
}

# Update production URLs
update_urls() {
    echo "🔗 Updating production URLs..."
    
    read -p "Enter your frontend URL (e.g., https://myapp.vercel.app): " frontend_url
    read -p "Enter your backend URL (e.g., https://myapi.onrender.com): " backend_url
    
    # Update frontend config
    sed -i.bak "s|https://emotion-music-api.onrender.com|$backend_url|g" frontend/config.js
    
    echo "✅ URLs updated!"
    echo "📌 Remember to:"
    echo "1. Set FRONTEND_URL=$frontend_url in backend environment"
    echo "2. Redeploy both frontend and backend"
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1) deploy_vercel ;;
        2) deploy_netlify ;;
        3) prepare_render ;;
        4) prepare_replit ;;
        5) setup_github ;;
        6) update_urls ;;
        7) echo "👋 Goodbye!"; exit 0 ;;
        *) echo "❌ Invalid option" ;;
    esac
done