"""
Verification agent re-runs tests after fixes.
"""

from agents.test_runner import TestRunner


class VerificationAgent:
    """
    Re-runs tests to verify if fixes resolved failures.
    """

    def __init__(self):
        self.tester = TestRunner()

    def verify(self, repo_path: str) -> int:
        """
        Re-run pytest and return remaining failure count.

        Args:
            repo_path (str): Path to cloned repository

        Returns:
            int: number of remaining failures
        """

        print("🔎 Verifying fixes by re-running tests...")

        failures = self.tester.run_tests(repo_path)

        if failures == 0:
            print("✅ All tests passing after fix iteration")
        else:
            print(f"❌ Remaining failures: {failures}")

        return failures