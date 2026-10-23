#!/bin/bash

echo "🔧 Setting up Git LFS for Agri-Guide models..."

# Check if git lfs is installed
if ! command -v git-lfs &> /dev/null; then
    echo "❌ Git LFS is not installed."
    echo "📥 Please install Git LFS first:"
    echo "   Windows: choco install git-lfs"
    echo "   macOS: brew install git-lfs"
    echo "   Linux: sudo apt install git-lfs"
    echo "   Or download from: https://git-lfs.github.com/"
    exit 1
fi

# Initialize Git LFS
echo "🚀 Initializing Git LFS..."
git lfs install

# Track model files
echo "📦 Tracking model files..."
git lfs track "*.pkl"
git lfs track "final_model/*.pkl"

# Update .gitignore to allow .pkl files
echo "📝 Updating .gitignore..."
sed -i.bak '/^\*.pkl$/d' .gitignore
sed -i.bak '/^# Model files (users should train their own)$/d' .gitignore
sed -i.bak '/^\*.pkl$/d' .gitignore

# Add files to git
echo "➕ Adding files to git..."
git add .gitattributes
git add *.pkl final_model/*.pkl

echo "✅ Git LFS setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Commit the changes: git commit -m 'Add model files with Git LFS'"
echo "2. Push to GitHub: git push origin main"
echo "3. Deploy to your chosen platform (Render, Railway, etc.)"
echo ""
echo "💡 Your model files will now be stored in Git LFS and can be deployed!"