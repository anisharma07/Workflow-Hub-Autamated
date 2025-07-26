#!/usr/bin/env python3
"""
GitHub Repository Automation Script

This script automates:
1. Pushing .github/workflows folder to the main branch of multiple repositories
2. Adding environment variables as repository secrets
3. Updating workflow permissions (read/write + PR creation/approval)

Prerequisites:
- GitHub Personal Access Token with repo and admin:repo_hook permissions
- Git configured with your credentials
- Python libraries: requests, python-dotenv, PyGithub

Usage:
1. Set GITHUB_TOKEN environment variable or update the script
2. Run: python automate.py
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Repository URLs
repo_urls = [
    "https://github.com/anisharma07/c4gt-website",
    "https://github.com/anisharma07/Invoice-PPT-Subscribe-Storacha-Storage",
    "https://github.com/anisharma07/web3-invoice-token-gated-storacha",
    # "https://github.com/anisharma07/web3-medical-invoice-storacha",
    # "https://github.com/anisharma07/fil-token-gated-dapp-advanced",
    # "https://github.com/anisharma07/web3-invoice-storacha-backend",
    # "https://github.com/anisharma07/storacha-image-hosting-service",
    # "https://github.com/anisharma07/py-multiaddr",
    # "https://github.com/anisharma07/web3-medical-incident-tools",
    # "https://github.com/anisharma07/drand.py",
    # "https://github.com/anisharma07/filosign",
    # "https://github.com/anisharma07/filecoin-services"
]

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("❌ Error: GITHUB_TOKEN environment variable not set!")
    print("Please set your GitHub Personal Access Token:")
    print("export GITHUB_TOKEN='your_token_here'")
    sys.exit(1)

GITHUB_API_BASE = "https://api.github.com"

# Secrets to add to repositories
SECRETS_TO_ADD = {
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_REGION': os.getenv('AWS_REGION'),
    'AWS_BEDROCK_MODEL_ID': os.getenv('AWS_BEDROCK_MODEL_ID')
}


class GitHubAutomation:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def extract_repo_info(self, repo_url: str) -> Tuple[str, str]:
        """Extract owner and repo name from GitHub URL"""
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]

        if repo_url.startswith('https://github.com/'):
            parts = repo_url.replace('https://github.com/', '').split('/')
        elif repo_url.startswith('git@github.com:'):
            parts = repo_url.replace('git@github.com:', '').split('/')
        else:
            raise ValueError(f"Invalid GitHub URL format: {repo_url}")

        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub URL format: {repo_url}")

        return parts[0], parts[1]

    def check_repo_exists(self, owner: str, repo: str) -> bool:
        """Check if repository exists and is accessible"""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        response = self.session.get(url)
        return response.status_code == 200

    def get_repo_public_key(self, owner: str, repo: str) -> Dict:
        """Get repository's public key for encrypting secrets"""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/secrets/public-key"
        response = self.session.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get public key: {response.status_code} - {response.text}")

    def encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """Encrypt a secret using the repository's public key"""
        try:
            from nacl import encoding, public
        except ImportError:
            print("❌ Error: PyNaCl library required for secret encryption")
            print("Install it with: pip install PyNaCl")
            sys.exit(1)

        public_key_obj = public.PublicKey(
            public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key_obj)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return encoding.Base64Encoder().encode(encrypted).decode("utf-8")

    def create_or_update_secret(self, owner: str, repo: str, secret_name: str, secret_value: str) -> bool:
        """Create or update a repository secret"""
        try:
            # Get public key
            public_key_data = self.get_repo_public_key(owner, repo)

            # Encrypt secret
            encrypted_value = self.encrypt_secret(
                public_key_data['key'], secret_value)

            # Create/update secret
            url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/secrets/{secret_name}"
            data = {
                'encrypted_value': encrypted_value,
                'key_id': public_key_data['key_id']
            }

            response = self.session.put(url, json=data)

            if response.status_code in [201, 204]:
                return True
            else:
                print(
                    f"   ❌ Failed to set secret {secret_name}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"   ❌ Error setting secret {secret_name}: {str(e)}")
            return False

    def update_workflow_permissions(self, owner: str, repo: str) -> bool:
        """Update repository workflow permissions to read/write and allow PR creation"""
        try:
            url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/permissions"

            # Set workflow permissions
            data = {
                "enabled": True,  # Enable GitHub Actions
                "default_workflow_permissions": "write",  # read or write
                "can_approve_pull_request_reviews": True
            }

            response = self.session.put(url, json=data)

            if response.status_code in [200, 204]:
                return True
            else:
                print(
                    f"   ❌ Failed to update workflow permissions: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"   ❌ Error updating workflow permissions: {str(e)}")
            return False

    def clone_repo(self, repo_url: str, temp_dir: str) -> str:
        """Clone repository to temporary directory"""
        owner, repo = self.extract_repo_info(repo_url)
        clone_url = f"https://{self.token}@github.com/{owner}/{repo}.git"

        repo_path = os.path.join(temp_dir, repo)

        try:
            # Store original working directory
            original_cwd = os.getcwd()

            subprocess.run([
                'git', 'clone', clone_url, repo_path
            ], check=True, capture_output=True, text=True, cwd=original_cwd)

            return repo_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to clone repository: {e.stderr}")

    def get_default_branch(self, repo_path: str) -> str:
        """Get the default branch name of the repository"""
        try:
            # Get the current branch name
            result = subprocess.run(['git', 'branch', '--show-current'],
                                    capture_output=True, text=True, check=True, cwd=repo_path)
            current_branch = result.stdout.strip()

            if current_branch:
                return current_branch

            # Fallback: try to get remote HEAD
            result = subprocess.run(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
                                    capture_output=True, text=True, cwd=repo_path)
            if result.returncode == 0:
                return result.stdout.strip().split('/')[-1]

            # Default fallbacks
            for branch in ['main', 'master']:
                result = subprocess.run(['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{branch}'],
                                        capture_output=True, cwd=repo_path)
                if result.returncode == 0:
                    return branch

            return 'main'  # Final fallback
        except:
            return 'main'

    def push_workflows(self, repo_path: str, workflows_source: str) -> bool:
        """Copy workflows and push to repository"""
        try:
            # Store original working directory
            original_cwd = os.getcwd()

            # Create .github/workflows directory if it doesn't exist
            workflows_dest = os.path.join(repo_path, '.github', 'workflows')
            os.makedirs(workflows_dest, exist_ok=True)

            # Copy workflow files
            for workflow_file in os.listdir(workflows_source):
                if workflow_file.endswith('.yml') or workflow_file.endswith('.yaml'):
                    src_file = os.path.join(workflows_source, workflow_file)
                    dest_file = os.path.join(workflows_dest, workflow_file)
                    shutil.copy2(src_file, dest_file)
                    print(f"   📋 Copied {workflow_file}")

            # Git operations using cwd parameter instead of os.chdir()
            # Add files
            subprocess.run(['git', 'add', '.github/workflows/'],
                           check=True, capture_output=True, cwd=repo_path)

            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'diff', '--cached', '--quiet'], capture_output=True, cwd=repo_path)
            if result.returncode == 0:
                print("   ℹ️  No changes to commit (workflows already up to date)")
                return True

            # Commit changes
            subprocess.run([
                'git', 'commit', '-m', 'Add/Update GitHub Actions workflows'
            ], check=True, capture_output=True, cwd=repo_path)

            # Get the default branch and push
            default_branch = self.get_default_branch(repo_path)
            print(f"   📤 Pushing to {default_branch} branch...")
            subprocess.run(['git', 'push', 'origin', default_branch],
                           check=True, capture_output=True, cwd=repo_path)

            return True

        except subprocess.CalledProcessError as e:
            print(
                f"   ❌ Git operation failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
            return False
        finally:
            # Always restore original working directory
            try:
                os.chdir(original_cwd)
            except:
                pass

    def process_repository(self, repo_url: str, workflows_source: str) -> Dict:
        """Process a single repository: push workflows and set secrets"""
        print(f"\n🔄 Processing repository: {repo_url}")

        try:
            owner, repo = self.extract_repo_info(repo_url)

            # Check if repository exists
            if not self.check_repo_exists(owner, repo):
                return {
                    'repo': repo_url,
                    'status': 'error',
                    'message': 'Repository not found or not accessible'
                }

            result = {
                'repo': repo_url,
                'status': 'success',
                'workflows_pushed': False,
                'secrets_added': {},
                'permissions_updated': False,
                'errors': []
            }

            # Create temporary directory for cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Clone repository
                    print("   📥 Cloning repository...")
                    repo_path = self.clone_repo(repo_url, temp_dir)

                    # Push workflows
                    print("   🚀 Pushing workflows...")
                    workflows_success = self.push_workflows(
                        repo_path, workflows_source)
                    result['workflows_pushed'] = workflows_success

                    if workflows_success:
                        print("   ✅ Workflows pushed successfully")
                    else:
                        result['errors'].append('Failed to push workflows')

                except Exception as e:
                    error_msg = f"Failed to process workflows: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    result['errors'].append(error_msg)

            # Set repository secrets
            print("   🔐 Setting repository secrets...")
            for secret_name, secret_value in SECRETS_TO_ADD.items():
                if secret_value:
                    success = self.create_or_update_secret(
                        owner, repo, secret_name, secret_value)
                    result['secrets_added'][secret_name] = success
                    if success:
                        print(f"   ✅ Secret {secret_name} set successfully")
                    else:
                        result['errors'].append(
                            f'Failed to set secret {secret_name}')
                else:
                    print(
                        f"   ⚠️  Skipping {secret_name} (value not found in environment)")
                    result['secrets_added'][secret_name] = False

            # Update workflow permissions
            print("   🔧 Updating workflow permissions...")
            permissions_success = self.update_workflow_permissions(owner, repo)
            result['permissions_updated'] = permissions_success
            if permissions_success:
                print("   ✅ Workflow permissions updated successfully")
                print("      - Read and write permissions enabled")
                print("      - GitHub Actions can create and approve pull requests")
            else:
                result['errors'].append(
                    'Failed to update workflow permissions')

            if result['errors']:
                result['status'] = 'partial'

            return result

        except Exception as e:
            return {
                'repo': repo_url,
                'status': 'error',
                'message': str(e)
            }


def main():
    """Main execution function"""
    print("🚀 GitHub Repository Automation Script")
    print("=" * 50)

    # Validate workflows directory
    workflows_dir = '.github/workflows'
    if not os.path.exists(workflows_dir):
        print(f"❌ Error: Workflows directory '{workflows_dir}' not found!")
        sys.exit(1)

    # Validate environment variables
    missing_vars = [key for key, value in SECRETS_TO_ADD.items() if not value]
    if missing_vars:
        print(
            f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("These secrets will be skipped.")

    # Initialize GitHub automation
    github_automation = GitHubAutomation(GITHUB_TOKEN)

    # Process all repositories
    results = []
    successful_repos = 0

    print(f"\n📋 Processing {len(repo_urls)} repositories...")

    for i, repo_url in enumerate(repo_urls, 1):
        print(f"\n[{i}/{len(repo_urls)}] " + "=" * 40)

        result = github_automation.process_repository(repo_url, workflows_dir)
        results.append(result)

        if result['status'] == 'success':
            successful_repos += 1

        # Add delay between repositories to avoid rate limiting
        if i < len(repo_urls):
            time.sleep(2)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 AUTOMATION SUMMARY")
    print("=" * 60)

    print(
        f"✅ Successfully processed: {successful_repos}/{len(repo_urls)} repositories")

    for result in results:
        repo_name = result['repo'].split('/')[-1]
        status_emoji = {
            'success': '✅',
            'partial': '⚠️ ',
            'error': '❌'
        }.get(result['status'], '❓')

        print(f"\n{status_emoji} {repo_name}")

        if result['status'] == 'error':
            print(f"   Error: {result.get('message', 'Unknown error')}")
        else:
            if 'workflows_pushed' in result:
                workflows_status = '✅' if result['workflows_pushed'] else '❌'
                print(f"   Workflows: {workflows_status}")

            if 'secrets_added' in result:
                secrets_success = sum(
                    1 for success in result['secrets_added'].values() if success)
                secrets_total = len(result['secrets_added'])
                print(f"   Secrets: {secrets_success}/{secrets_total} added")

            if 'permissions_updated' in result:
                permissions_status = '✅' if result['permissions_updated'] else '❌'
                print(f"   Workflow Permissions: {permissions_status}")

            if result.get('errors'):
                print(f"   Errors: {', '.join(result['errors'])}")

    print(f"\n🎉 Automation completed!")


if __name__ == "__main__":
    main()
