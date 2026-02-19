"""
Handles repository cloning and preparation.
"""

import os
import subprocess
import shutil
from urllib.parse import urlparse


class RepoAnalyzer:
    """Handles repository cloning and preparation."""

    def clone_repository(self, repo_url):
        """
        Clone a public GitHub repository using HTTPS.
        Returns local repo path.
        """

        print(f"📦 Cloning repository: {repo_url}")

        if not repo_url.startswith("https://"):
            raise Exception("Only HTTPS GitHub URLs are supported.")

        # Extract repo name from URL
        parsed = urlparse(repo_url)
        repo_name = os.path.basename(parsed.path).replace(".git", "")

        clone_path = os.path.join(os.getcwd(), repo_name)

        # Remove existing folder if already exists (clean state)
        if os.path.exists(clone_path):
            print("⚠️ Repo already exists locally. Removing old copy...")
            shutil.rmtree(clone_path)

        try:
            subprocess.run(
                ["git", "clone", repo_url, clone_path],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git clone failed: {e}")

        print(f"✅ Repository cloned at: {clone_path}")

        return clone_path