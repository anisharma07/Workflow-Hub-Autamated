# GitHub Repository Automation Script

## 📚 Quick Navigation

- 🚀 **[Quick Setup Guide](./QUICK_SETUP_DOC.md)** - Get started in 5 minutes
- 📖 **[Workflows Documentation](./WORKFLOWS_DOC.md)** - Detailed workflow explanations

---

This automation script helps you efficiently manage multiple GitHub repositories by:

1. **Pushing `.github/workflows` folder** to the main branch of multiple repositories
2. **Adding environment variables as repository secrets** to enable GitHub Actions

## Features

- ✅ **Batch Processing**: Handle multiple repositories at once
- ✅ **Error Handling**: Proper handling for existing files and secrets
- ✅ **Conflict Resolution**: Skip unchanged files, update existing secrets
- ✅ **Rate Limiting**: Built-in delays to respect GitHub API limits
- ✅ **Detailed Reporting**: Comprehensive success/failure reporting
- ✅ **Security**: Encrypted secret handling using GitHub's public key encryption

## Prerequisites

### 1. GitHub Personal Access Token

You need a GitHub Personal Access Token with the following permissions:

- `repo` (Full control of private repositories)
- `admin:repo_hook` (Admin access to repository hooks)

**To create a token:**

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select the required scopes: `repo` and `admin:repo_hook`
4. Copy the generated token

### 2. Git Configuration

Ensure Git is configured with your credentials:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Python Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

## Setup Instructions

### 1. Environment Variables

Create a `.env` file with your secrets:

```bash
# Copy the example file and edit with your values
cp .env.example .env
```

Then edit `.env` with your actual values:

```properties
GITHUB_TOKEN='your_github_personal_access_token_here'
AWS_ACCESS_KEY_ID="your_aws_access_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
AWS_REGION="us-east-1"
AWS_BEDROCK_MODEL_ID='us.anthropic.claude-sonnet-4-20250514-v1:0'
```

### 2. GitHub Token

Set your GitHub token as an environment variable:

**Option A: Export in terminal (temporary)**

```bash
export GITHUB_TOKEN='your_github_token_here'
```

**Option B: Add to .env file (recommended)**
Add this line to your `.env` file:

```properties
GITHUB_TOKEN='your_github_token_here'
```

**Option C: Add to shell profile (permanent)**
Add to `~/.zshrc` or `~/.bashrc`:

```bash
export GITHUB_TOKEN='your_github_token_here'
```

### 3. Verify Workflows Directory

Ensure your `.github/workflows` directory contains the workflow files:

```
.github/
└── workflows/
    ├── claude-generate.yml
    ├── claude-organize.yml
    └── claude-pr-review.yml
```

## Usage

### Run the Automation Script

```bash
python automate.py
```

### What the Script Does

1. **Validates Prerequisites**

   - Checks for GitHub token
   - Verifies workflows directory exists
   - Validates environment variables

2. **For Each Repository:**

   - Clones the repository to a temporary directory
   - Copies workflow files to `.github/workflows/`
   - Commits and pushes changes to main branch
   - Encrypts and adds secrets to repository settings

3. **Provides Detailed Feedback**
   - Progress updates for each repository
   - Success/failure status for workflows and secrets
   - Final summary report

### Example Output

```
🚀 GitHub Repository Automation Script
==================================================

📋 Processing 12 repositories...

[1/12] ========================================
🔄 Processing repository: https://github.com/anisharma07/c4gt-website

   📥 Cloning repository...
   🚀 Pushing workflows...
   📋 Copied claude-generate.yml
   📋 Copied claude-organize.yml
   📋 Copied claude-pr-review.yml
   ✅ Workflows pushed successfully
   🔐 Setting repository secrets...
   ✅ Secret AWS_ACCESS_KEY_ID set successfully
   ✅ Secret AWS_SECRET_ACCESS_KEY set successfully
   ✅ Secret AWS_REGION set successfully
   ✅ Secret AWS_BEDROCK_MODEL_ID set successfully

[2/12] ========================================
...

============================================================
📊 AUTOMATION SUMMARY
============================================================
✅ Successfully processed: 12/12 repositories

✅ c4gt-website
   Workflows: ✅
   Secrets: 4/4 added

✅ Invoice-PPT-Subscribe-Storacha-Storage
   Workflows: ✅
   Secrets: 4/4 added

🎉 Automation completed!
```

## Error Handling

The script handles various scenarios:

- **Repository Access Issues**: Checks if repo exists and is accessible
- **Existing Files**: Updates workflows if they already exist
- **Existing Secrets**: Updates secret values if they already exist
- **Network Issues**: Includes retry logic and rate limiting
- **Permission Issues**: Clear error messages for insufficient permissions

## Security Considerations

- **Token Security**: Store GitHub token securely, never commit to repository
- **Secret Encryption**: All secrets are encrypted using GitHub's public key before transmission
- **Temporary Cloning**: Repositories are cloned to temporary directories and cleaned up automatically
- **API Rate Limiting**: Built-in delays prevent hitting GitHub API rate limits

## Troubleshooting

### Common Issues

1. **"Repository not found or not accessible"**

   - Verify repository URLs are correct
   - Ensure GitHub token has access to the repositories
   - Check if repositories are private and token has appropriate permissions

2. **"Failed to push workflows"**

   - Verify you have push access to the repositories
   - Check if main branch is protected and requires pull requests
   - Ensure Git is configured with correct credentials

3. **"Failed to set secret"**

   - Verify GitHub token has `admin:repo_hook` permissions
   - Check if repository has restrictions on secrets
   - Ensure secret values are valid

4. **"PyNaCl library required"**

   ```bash
   pip install PyNaCl
   ```

5. **Rate Limiting**
   - The script includes built-in delays
   - If you hit rate limits, wait and try again
   - Consider processing repositories in smaller batches

### Getting Help

- Check the detailed error messages in the script output
- Verify all prerequisites are met
- Ensure GitHub token permissions are correct
- Test with a single repository first

## Customization

### Adding More Secrets

To add more secrets, update the `SECRETS_TO_ADD` dictionary in `automate.py`:

```python
SECRETS_TO_ADD = {
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_REGION': os.getenv('AWS_REGION'),
    'AWS_BEDROCK_MODEL_ID': os.getenv('AWS_BEDROCK_MODEL_ID'),
    'NEW_SECRET': os.getenv('NEW_SECRET')
}
```

### Processing Subset of Repositories

To process only specific repositories, modify the `repo_urls` list:

```python
repo_urls = [
    "https://github.com/anisharma07/specific-repo1",
    "https://github.com/anisharma07/specific-repo2"
]
```

### Different Branch

To push to a different branch, modify the push command in the `push_workflows` method:

```python
subprocess.run(['git', 'push', 'origin', 'your-branch'], check=True, capture_output=True)
```

## License

This automation script is provided as-is for repository management purposes.

# workflow-automated-upload
