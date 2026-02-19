"""
Main orchestration engine for multi-agent debugging workflow.
"""

import concurrent.futures
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime

from core.retry_controller import RetryController
from agents.repo_analyzer import RepoAnalyzer
from agents.test_runner import TestRunner
from agents.bug_classifier import BugClassifier
from agents.fix_generator import FixGenerator
from agents.verification import VerificationAgent
from agents.git_manager import GitManager
from crewai import Agent, Task, Crew


def run_agent(repo_url, team_name, leader_name, retry_limit=None):
    """
    Runs the multi-agent debugging workflow.
    """

    start_time = time.time()
    print("\n🚀 Starting AI Debug Orchestrator\n")

    analyzer = RepoAnalyzer()
    tester = TestRunner()
    classifier = BugClassifier()
    fixer = FixGenerator()
    verifier = VerificationAgent()
    git_manager = GitManager()
    if retry_limit is None:
        retry_limit = int(os.getenv("RETRY_LIMIT", "5"))
    controller = RetryController(retry_limit)

    timeline = []
    all_fixes = []
    total_failures = 0

    # -----------------------------
    # CrewAI Planning
    # -----------------------------
    os.environ.setdefault("CI", "true")
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
    os.environ.setdefault("CREWAI_TELEMETRY_DISABLED", "true")
    os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")

    if not os.getenv("GOOGLE_API_KEY"):
        raise Exception("GOOGLE_API_KEY not set for CrewAI")

    model_name = os.getenv("MODEL") or os.getenv("MODEL_NAME") or "gemini/gemini-1.5-pro"

    planner = Agent(
        role="DevOps Planner",
        goal="Outline a minimal fix plan for the repo",
        backstory="Senior DevOps agent coordinating tests and fixes",
        verbose=False,
        allow_delegation=False,
        llm=model_name,
    )

    plan_task = Task(
        description=(
            "Given repo URL {repo_url}, team {team_name}, leader {leader_name}, "
            "return a short plan of steps to detect failures and apply fixes."
        ),
        expected_output="A short step-by-step plan",
        agent=planner,
    )

    crew = Crew(
        agents=[planner],
        tasks=[plan_task],
        verbose=False,
    )
    crew_timeout = int(os.getenv("CREWAI_TIMEOUT", "30"))
    run_crewai_planning(crew, crew_timeout, {
        "repo_url": repo_url,
        "team_name": team_name,
        "leader_name": leader_name,
    })

    # -----------------------------
    # Clone repository
    # -----------------------------
    repo_path = analyzer.clone_repository(repo_url)

    # -----------------------------
    # Branch creation
    # -----------------------------
    branch_name = git_manager.create_branch_name(team_name, leader_name)

    # -----------------------------
    # Initial test run
    # -----------------------------
    failures = tester.run_tests(repo_path)
    total_failures = failures

    # -----------------------------
    # Retry Loop
    # -----------------------------
    while controller.should_retry():
        print(f"\n🔁 Iteration {controller.iteration}")

        if failures == 0:
            timeline.append({
                "iteration": controller.iteration,
                "failures": 0,
                "fixesApplied": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "passed",
                "retryLimit": retry_limit,
            })

            ensure_github_actions(repo_path)
            git_manager.prepare_and_push(repo_path, branch_name, repo_url)
            ci_status = poll_ci_cd(repo_url, branch_name)
            timeline[-1]["ci_status"] = ci_status

            result = build_final_result(
                repo_url,
                branch_name,
                total_failures,
                all_fixes,
                timeline,
                start_time,
                retry_limit,
            )

            write_results_json(result)
            return result

        failure_data = tester.collect_failures(repo_path)
        bug_types = classifier.classify(failure_data)

        fix_list = fixer.generate_fixes(repo_path, bug_types)
        all_fixes.extend(fix_list)

        failures = verifier.verify(repo_path)

        timeline.append({
            "iteration": controller.iteration,
            "failures": failures,
            "fixesApplied": len(fix_list),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "passed" if failures == 0 else "failed",
            "retryLimit": retry_limit,
        })

        controller.next()

    result = build_final_result(
        repo_url,
        branch_name,
        total_failures,
        all_fixes,
        timeline,
        start_time,
        retry_limit,
    )

    write_results_json(result)
    return result


# ==========================================================
# Helper Functions
# ==========================================================

def build_final_result(repo_url, branch_name, total_failures, fixes, timeline, start_time, retry_limit):
    end_time = time.time()
    total_time = int(end_time - start_time)

    commit_count = len(timeline)
    base_score = 100
    penalty = max(commit_count - 20, 0) * 2
    speed_bonus = 10 if total_time < 300 else 0
    final_score = max(base_score - penalty + speed_bonus, 0)

    last_status = timeline[-1].get("ci_status") or timeline[-1].get("status")
    ci_status = "passed" if str(last_status).lower() == "passed" else "failed"

    return {
        "status": "completed",
        "branch": branch_name,
        "total_failures": total_failures,
        "fixes_applied": len(fixes),
        "ci_status": ci_status,
        "fixes": fixes,
        "timeline": timeline,
        "score": {
            "base": base_score,
            "speedBonus": speed_bonus,
            "penalty": penalty,
            "finalScore": final_score
        },
        "total_time": total_time,
        "repository": repo_url,
        "commit_count": commit_count,
        "retry_limit": retry_limit
    }


def poll_ci_cd(repo_url, branch_name, max_wait_seconds=None, interval_seconds=None):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "FAILED"

    repo_info = parse_github_repo(repo_url)
    if not repo_info:
        return "FAILED"

    owner, repo = repo_info
    max_wait_seconds = int(os.getenv("CI_POLL_MAX_WAIT", "180")) if max_wait_seconds is None else max_wait_seconds
    interval_seconds = int(os.getenv("CI_POLL_INTERVAL", "15")) if interval_seconds is None else interval_seconds
    empty_limit = int(os.getenv("CI_POLL_EMPTY_LIMIT", "3"))
    empty_checks = 0
    deadline = time.time() + max_wait_seconds

    while time.time() < deadline:
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?branch={branch_name}"
        request = urllib.request.Request(url)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/vnd.github+json")

        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))

        runs = data.get("workflow_runs", [])
        if not runs:
            empty_checks += 1
            if empty_checks >= empty_limit:
                return "SKIPPED"
            time.sleep(interval_seconds)
            continue

        latest = runs[0]
        status = latest.get("status")
        conclusion = latest.get("conclusion")

        if status == "completed":
            if conclusion == "success":
                return "PASSED"
            return "FAILED"

        time.sleep(interval_seconds)

    return "FAILED"


def parse_github_repo(repo_url):
    parsed = urllib.parse.urlparse(repo_url)
    path = parsed.path.strip("/")
    if not path:
        return None

    parts = path.split("/")
    if len(parts) < 2:
        return None

    repo = parts[1].replace(".git", "")
    return parts[0], repo


def run_crewai_planning(crew, timeout_seconds, inputs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(crew.kickoff, inputs=inputs)
        try:
            future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            return


def ensure_github_actions(repo_path):
    workflows_dir = os.path.join(repo_path, ".github", "workflows")
    if os.path.isdir(workflows_dir):
        for name in os.listdir(workflows_dir):
            if name.endswith(".yml") or name.endswith(".yaml"):
                if name != "ci.yml":
                    return

    os.makedirs(workflows_dir, exist_ok=True)
    workflow_path = os.path.join(workflows_dir, "ci.yml")
    if os.path.exists(workflow_path):
        with open(workflow_path, "r", encoding="utf-8") as handle:
            existing = handle.read()
        if "Generated by Autonomous DevOps Agent" not in existing and not existing.startswith("name: CI"):
            return

    workflow = (
        "# Generated by Autonomous DevOps Agent\n"
        "name: CI\n\n"
        "on:\n  push:\n    branches: ['**']\n\n"
        "jobs:\n  tests:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.11'\n"
        "      - name: Install deps\n        run: |\n          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi\n          pip install pytest\n"
        "      - name: Run tests\n        run: |\n          set +e\n          python -m pytest\n          status=$?\n          if [ $status -eq 5 ]; then exit 0; fi\n          exit $status\n"
    )

    with open(workflow_path, "w", encoding="utf-8") as handle:
        handle.write(workflow)


def write_results_json(result_dict):
    try:
        with open("results.json", "w") as f:
            json.dump(result_dict, f, indent=2)
        print("📄 results.json generated successfully")
    except Exception as e:
        print("⚠️ Failed to write results.json:", e)