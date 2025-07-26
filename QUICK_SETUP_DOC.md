# 🚀 Quick Setup Guide

## What This Script Does

1. **📋 Workflow Code Push** - Copies `.github/workflows` to all your repositories
2. **🔧 Add Workflow Permissions** - Enables read/write permissions for GitHub Actions
3. **🔐 Add AWS Secrets** - Uploads your AWS credentials from `.env` to repository secrets

---

## ⚡ Quick Setup Steps

### Step 1: Clone This Repository

```bash
https://github.com/anisharma07/Workflows-Upload-Automated.git
cd Workflows-Upload-Automated
```

### Step 2: Create GitHub Classic Token

Go to: **[GitHub Settings → Tokens (Classic)](https://github.com/settings/tokens)**

- Click "Generate new token (classic)"
- **Required Permissions/Scopes:**
  - ✅ **`repo`** - Full control of private repositories
    - Enables: repo:status, repo_deployment, public_repo, repo:invite, security_events
  - ✅ **`admin:repo_hook`** - Admin access to repository hooks
    - Enables: write:repo_hook, read:repo_hook
- Set expiration (recommended: 7 days or custom)
- Click "Generate token"
- **⚠️ Copy the token immediately** (you won't see it again!)

### Step 3: Add Your Repository URLs

Edit `automate.py` - find `repo_urls` list and add your repositories:

```python
repo_urls = [
    "https://github.com/YOUR_USERNAME/repo1",
    "https://github.com/YOUR_USERNAME/repo2",
    "https://github.com/YOUR_USERNAME/repo3",
]
```

⚠️ **Make sure you own these repositories!**

### Step 4: Create .env File

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
GITHUB_TOKEN='your_github_token_here'
AWS_ACCESS_KEY_ID="your_aws_access_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
AWS_REGION="us-east-1"
AWS_BEDROCK_MODEL_ID='us.anthropic.claude-sonnet-4-20250514-v1:0'
```

### Step 5: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 6: Make Setup Script Executable

```bash
chmod +x setup.sh
```

### Step 7: Run Setup

```bash
./setup.sh
```

### Step 8: Run Automation

```bash
python3 automate.py
```

---

## 🎯 Expected Results

- ✅ Workflows pushed to all repositories
- ✅ GitHub Actions permissions enabled
- ✅ AWS secrets added to repository settings
- ✅ Ready to use Claude workflows!

---

## 🆘 Quick Troubleshooting

| Issue                  | Solution                                            |
| ---------------------- | --------------------------------------------------- |
| `Permission denied`    | Check token permissions: `repo` + `admin:repo_hook` |
| `Repository not found` | Verify you own the repositories in `repo_urls`      |
| `Missing dependencies` | Run: `pip install -r requirements.txt`              |

---

**Need detailed docs?** → See [README.md](./README.md)
