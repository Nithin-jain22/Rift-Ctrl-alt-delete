"""
Controls retry logic for orchestration iterations.
"""


class RetryController:
    """Manages retry iterations."""

    def __init__(self, limit):
        self.limit = limit
        self.iteration = 1

    def should_retry(self):
        """Check if retries are allowed."""
        return self.iteration <= self.limit

    def next(self):
        """Move to next iteration."""
        self.iteration += 1
