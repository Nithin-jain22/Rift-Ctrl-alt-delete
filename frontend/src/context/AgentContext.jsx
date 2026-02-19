import { createContext, useContext, useMemo, useState } from "react";
import axios from "axios";

const AgentContext = createContext();

export function AgentProvider({ children }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [runSummary, setRunSummary] = useState(null);
  const [score, setScore] = useState(null);
  const [fixes, setFixes] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [retryLimit, setRetryLimit] = useState(null);

  const runAgent = async ({ githubUrl, teamName, leaderName }) => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setRunSummary(null);
      setScore(null);
      setFixes([]);
      setTimeline([]);
      setRetryLimit(null);

      // Step 1: Trigger backend
      const response = await axios.post("http://127.0.0.1:8000/run-agent", {
        githubUrl,
        teamName,
        leaderName,
      });

      const jobId = response.data.jobId;

      // Step 2: Poll status
      const interval = setInterval(async () => {
        const statusRes = await axios.get(
          `http://127.0.0.1:8000/status/${jobId}`
        );

        const payload = statusRes.data || {};
        const summary = payload.runSummary || {};
        const mappedSummary = {
          repository: summary.repository || payload.repository,
          branch: summary.branch || payload.branch,
          team_name: summary.teamName || payload.team_name,
          leader_name: summary.leaderName || payload.leader_name,
          total_failures: summary.totalFailures ?? payload.total_failures,
          fixes_applied: summary.fixesApplied ?? payload.fixes_applied,
          ci_status: summary.ciStatus || payload.ci_status,
          time_taken: summary.totalTime ?? payload.total_time,
        };

        const rawScore = payload.score || {};
        const mappedScore = {
          base: rawScore.base,
          speed_bonus: rawScore.speedBonus ?? rawScore.speed_bonus,
          efficiency_penalty: rawScore.penalty ?? rawScore.efficiency_penalty,
          final_score: rawScore.finalScore ?? rawScore.final_score,
        };

        const mappedTimeline = Array.isArray(payload.timeline)
          ? payload.timeline.map((item) => ({
              ...item,
              ci_status: (item.ci_status || item.status || "").toUpperCase(),
              retry_limit: item.retryLimit ?? payload.retryLimit ?? payload.retry_limit,
            }))
          : [];

        setRunSummary(Object.values(mappedSummary).some((val) => val !== undefined) ? mappedSummary : null);
        setScore(Object.values(mappedScore).some((val) => val !== undefined) ? mappedScore : null);
        const mappedFixes = Array.isArray(payload.fixes)
          ? payload.fixes.map((fix) => ({
              file: fix.file,
              bug_type: fix.bug_type || fix.bugType,
              line: fix.line,
              commit_message: fix.commit_message || fix.commitMessage,
              status: fix.status,
            }))
          : [];

        setFixes(mappedFixes);
        setTimeline(mappedTimeline);
        setRetryLimit(payload.retryLimit ?? payload.retry_limit ?? null);

        if (
          payload.status === "completed" ||
          payload.status === "failed"
        ) {
          clearInterval(interval);
          setResult(payload);
          setLoading(false);
          if (payload.status === "failed") {
            setError(payload.error || "Run failed");
          }
        }
      }, 5000);

    } catch (err) {
      setError("Failed to run agent");
      setLoading(false);
    }
  };

  const value = useMemo(
    () => ({
      runAgent,
      loading,
      error,
      result,
      runSummary,
      score,
      fixes,
      timeline,
      retryLimit,
    }),
    [runAgent, loading, error, result, runSummary, score, fixes, timeline, retryLimit]
  );

  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
}

export function useAgent() {
  return useContext(AgentContext);
}