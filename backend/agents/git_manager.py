"""
Handles git branch creation and push operations.
"""

import os
import subprocess
import re


class GitManager:
    """Manages git operations including branch creation and push."""

    def create_branch_name(self, team_name: str, leader_name: str) -> str:
        clean_team = re.sub(r'[^A-Za-z0-9 ]', '', team_name)
        clean_leader = re.sub(r'[^A-Za-z0-9 ]', '', leader_name)

        team_part = clean_team.upper().replace(" ", "_")
        leader_part = clean_leader.upper().replace(" ", "_")

        branch = f"{team_part}_{leader_part}_AI_Fix"
        print(f"🌿 Branch prepared: {branch}")
        return branch

    def prepare_and_push(self, repo_path: str, branch_name: str, repo_url: str):
        print("📦 Creating branch and pushing to GitHub...")

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise Exception("GITHUB_TOKEN not set")

        if not repo_url.startswith("https://"):
            raise Exception("Only HTTPS repositories supported")

        auth_repo_url = repo_url.replace(
            "https://",
            f"https://{token}@"
        )

        try:
            # Create or reuse branch
            create_branch = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if create_branch.returncode != 0:
                subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=repo_path,
                    check=True
                )

            # Stage files
            subprocess.run(
                ["git", "add", "."],
                cwd=repo_path,
                check=True
            )

            # Try commit (DO NOT crash if nothing to commit)
            commit_process = subprocess.run(
                ["git", "commit", "-m", "[AI-AGENT] Automated fixes applied"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )

            if commit_process.returncode != 0:
                print("⚠️ Commit skipped (likely nothing to commit).")

            # Set remote with token
            subprocess.run(
                ["git", "remote", "set-url", "origin", auth_repo_url],
                cwd=repo_path,
                check=True
            )

            # Push branch (force-with-lease to update existing branch safely)
            push_process = subprocess.run(
                ["git", "push", "--force-with-lease", "origin", branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True
            )

            print("PUSH STDOUT:", push_process.stdout)
            print("PUSH STDERR:", push_process.stderr)

            if push_process.returncode != 0:
                raise Exception(push_process.stderr)

            print("✅ Branch pushed successfully!")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Git operation failed: {e}")