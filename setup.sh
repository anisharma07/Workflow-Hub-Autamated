#!/bin/bash

echo "🚀 Setting up GitHub Repository Automation"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env file exists and has GitHub token
if [ -f ".env" ]; then
    if grep -q "GITHUB_TOKEN='your_github_personal_access_token_here'" .env; then
        echo ""
        echo "⚠️  IMPORTANT: Update your GitHub token in .env file"
        echo "   Replace 'your_github_personal_access_token_here' with your actual token"
        echo ""
        echo "🔗 Get your token at: https://github.com/settings/tokens"
        echo "   Required permissions: repo, admin:repo_hook"
    else
        echo "✅ GitHub token appears to be configured in .env"
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update GITHUB_TOKEN in .env file with your personal access token"
echo "2. Run the automation: python3 automate.py"
echo ""
echo "For detailed instructions, see README.md"
