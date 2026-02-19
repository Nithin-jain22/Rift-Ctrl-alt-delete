"""
Parses pytest output and classifies bug types.
"""

import re


class BugClassifier:
    """
    Classifies failures into required hackathon bug types:
    LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, INDENTATION
    """

    def classify(self, pytest_output: str):
        """
        Parses pytest output and returns structured bug list.

        Returns:
            list of dict:
            [
                {
                    "file": "src/utils.py",
                    "bugType": "LINTING",
                    "line": 15,
                    "message": "Unused import os"
                }
            ]
        """

        bugs = []

        # ----------------------------------------
        # Regex to extract file and line
        # Example: src/utils.py:15: ...
        # ----------------------------------------
        pattern = r"([\w\/\.\-]+\.py):(\d+):"

        matches = re.finditer(pattern, pytest_output)

        for match in matches:
            file_path = match.group(1)
            line_number = int(match.group(2))

            # Extract surrounding error message
            line_start = match.start()
            snippet = pytest_output[line_start:line_start + 200]

            bug_type = self._detect_bug_type(snippet)

            bugs.append({
                "file": file_path,
                "bugType": bug_type,
                "line": line_number,
                "message": snippet.strip()
            })

        print(f"🔍 Classified {len(bugs)} bugs")
        return bugs


    # ==========================================================
    # Internal Detection Logic
    # ==========================================================

    def _detect_bug_type(self, error_snippet: str) -> str:
        lower = error_snippet.lower()

        if "unused import" in lower:
            return "LINTING"

        if "syntaxerror" in lower or "invalid syntax" in lower:
            return "SYNTAX"

        if "typeerror" in lower:
            return "TYPE_ERROR"

        if "indentationerror" in lower:
            return "INDENTATION"

        if "importerror" in lower or "modulenotfounderror" in lower:
            return "IMPORT"

        if "assert" in lower:
            return "LOGIC"

        # Default fallback
        return "LOGIC"