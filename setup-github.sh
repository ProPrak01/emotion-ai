#!/bin/bash

echo "🚀 GitHub Repository Setup for Emotion Music Generator"
echo "===================================================="
echo ""

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected!"
    echo ""
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "📝 Creating repository..."
        
        # Create repository
        gh repo create emotion-music-generator \
            --public \
            --description "Real-time emotion detection system that generates adaptive music based on facial expressions" \
            --homepage "https://emotion-music-generator.vercel.app" \
            --clone=false \
            --add-readme=false
        
        # Add remote
        git remote add origin "https://github.com/$(gh api user -q .login)/emotion-music-generator.git"
        
        # Push code
        echo "📤 Pushing code to GitHub..."
        git push -u origin main
        
        echo ""
        echo "✅ Repository created and code pushed!"
        echo "🔗 View your repository: https://github.com/$(gh api user -q .login)/emotion-music-generator"
        
    else
        echo "❌ Not authenticated with GitHub CLI"
        echo "Run: gh auth login"
    fi
else
    echo "❌ GitHub CLI not found"
    echo ""
    echo "Option 1: Install GitHub CLI"
    echo "  macOS: brew install gh"
    echo "  Linux: See https://github.com/cli/cli#installation"
    echo ""
    echo "Option 2: Manual setup"
    echo "  1. Go to https://github.com/new"
    echo "  2. Repository name: emotion-music-generator"
    echo "  3. Description: Real-time emotion detection system that generates adaptive music based on facial expressions"
    echo "  4. Make it Public"
    echo "  5. Don't initialize with README"
    echo "  6. Create repository"
    echo ""
    echo "Then run these commands:"
    echo ""
    echo "git remote add origin https://github.com/YOUR_USERNAME/emotion-music-generator.git"
    echo "git push -u origin main"
fi

echo ""
echo "📋 Next Steps:"
echo "1. ✅ GitHub repository created"
echo "2. 🎨 Deploy frontend to Vercel/Netlify"
echo "3. 🔧 Deploy backend to Render"
echo "4. 🔗 Update environment variables"