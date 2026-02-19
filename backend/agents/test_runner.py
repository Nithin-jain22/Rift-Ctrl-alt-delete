"""
Runs pytest and gathers failure information.
"""

import os
import subprocess


class TestRunner:
    """Executes pytest and parses results."""

    def _docker_command(self, repo_path, command):
        return [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{repo_path}:/workspace",
            "-w",
            "/workspace",
            "python:3.11-slim",
            "bash",
            "-lc",
            command,
        ]

    def _run_in_docker(self, repo_path, command):
        if not os.path.isdir(repo_path):
            raise Exception("Repository path not found")

        docker_cmd = self._docker_command(repo_path, command)
        return subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True
        )

    def run_tests(self, repo_path):
        """Run pytest and return number of failures."""
        print("🧪 Running tests...")

        command = "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi; pip install pytest; python -m pytest"
        result = self._run_in_docker(repo_path, command)

        output = result.stdout + result.stderr
        print(output)

        # If pytest not installed or execution failed badly
        if result.returncode != 0 and "No module named pytest" in output:
            raise Exception("pytest is not installed in the environment")

        # If pytest ran but tests failed
        if result.returncode != 0:
            return self._parse_failures(output)

        # Tests passed
        return 0

    def collect_failures(self, repo_path):
        """Collect full pytest output."""
        command = "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi; pip install pytest; python -m pytest"
        result = self._run_in_docker(repo_path, command)
        return result.stdout + result.stderr

    def _parse_failures(self, output):
        """Extract number of failed tests."""
        for line in output.splitlines():
            if "failed" in line.lower():
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        return int(part)
        return 0