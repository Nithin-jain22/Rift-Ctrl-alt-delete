"""
Generates structured fixes for detected bug types.
"""

import os
import subprocess


class FixGenerator:
    """Applies basic automated fixes and returns structured fix data."""

    def generate_fixes(self, repo_path, bug_types):
        """
        Apply fixes based on bug_types list.

        Args:
            repo_path (str)
            bug_types (list of dict):
                {
                    "file": "src/utils.py",
                    "bugType": "LINTING",
                    "line": 15,
                    "message": "Unused import os"
                }

        Returns:
            list: structured fix dictionaries
        """

        print("🛠️ Generating structured fixes...")

        structured_fixes = []

        for bug in bug_types:
            file_path = os.path.join(repo_path, bug["file"])

            if not os.path.exists(file_path):
                structured_fixes.append({
                    "file": bug["file"],
                    "bugType": bug["bugType"],
                    "line": bug["line"],
                    "commitMessage": "[AI-AGENT] File not found",
                    "status": "Failed"
                })
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                line_index = bug["line"] - 1
                commit_message = ""
                fix_applied = False

                # ----------------------------
                # LINTING — Remove unused import
                # ----------------------------
                if bug["bugType"] == "LINTING":
                    if 0 <= line_index < len(lines):
                        removed_line = lines.pop(line_index)
                        commit_message = f"[AI-AGENT] Removed unused import"
                        fix_applied = True

                # ----------------------------
                # SYNTAX — Add missing colon
                # ----------------------------
                elif bug["bugType"] == "SYNTAX":
                    if 0 <= line_index < len(lines):
                        if not lines[line_index].strip().endswith(":"):
                            lines[line_index] = lines[line_index].rstrip("\n") + ":\n"
                            commit_message = f"[AI-AGENT] Added missing colon"
                            fix_applied = True

                # ----------------------------
                # INDENTATION — Basic indent fix
                # ----------------------------
                elif bug["bugType"] == "INDENTATION":
                    if 0 <= line_index < len(lines):
                        lines[line_index] = "    " + lines[line_index].lstrip()
                        commit_message = f"[AI-AGENT] Fixed indentation"
                        fix_applied = True

                # ----------------------------
                # IMPORT — Add missing import placeholder
                # ----------------------------
                elif bug["bugType"] == "IMPORT":
                    lines.insert(0, "import os\n")
                    commit_message = f"[AI-AGENT] Added missing import"
                    fix_applied = True

                # ----------------------------
                # TYPE_ERROR / LOGIC (basic placeholder)
                # ----------------------------
                else:
                    commit_message = f"[AI-AGENT] Attempted automated fix"
                    fix_applied = False

                if fix_applied:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)

                    structured_fixes.append({
                        "file": bug["file"],
                        "bugType": bug["bugType"],
                        "line": bug["line"],
                        "commitMessage": commit_message,
                        "status": "Fixed"
                    })
                else:
                    structured_fixes.append({
                        "file": bug["file"],
                        "bugType": bug["bugType"],
                        "line": bug["line"],
                        "commitMessage": commit_message,
                        "status": "Failed"
                    })

            except Exception as e:
                structured_fixes.append({
                    "file": bug["file"],
                    "bugType": bug["bugType"],
                    "line": bug["line"],
                    "commitMessage": "[AI-AGENT] Fix failed",
                    "status": "Failed"
                })

        # ----------------------------------------
        # Stage & Commit All Fixes
        # ----------------------------------------
        try:
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)

            commit_process = subprocess.run(
                ["git", "commit", "-m", "[AI-AGENT] Automated fixes applied"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )

            if commit_process.returncode != 0:
                if "nothing to commit" not in commit_process.stderr.lower():
                    print("⚠️ Commit warning:", commit_process.stderr)

        except Exception as e:
            print("⚠️ Git commit error:", e)

        print(f"✅ Fix generation complete: {len(structured_fixes)} fixes processed")

        return structured_fixes