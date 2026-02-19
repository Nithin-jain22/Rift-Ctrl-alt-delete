import { useAgent } from "../context/AgentContext";

export default function RunSummaryCard() {
  const { runSummary } = useAgent();

  if (!runSummary) return null;

  const {
    repository,
    branch,
    team_name,
    leader_name,
    total_failures,
    fixes_applied,
    ci_status,
    time_taken,
  } = runSummary;

  const status = (ci_status || "").toUpperCase();

  return (
    <div className="bg-white p-6 rounded-xl shadow-md space-y-2">
      <h2 className="text-xl font-semibold text-gray-700">Run Summary</h2>

      <p><strong>Repository:</strong> {repository}</p>
      <p><strong>Team Name:</strong> {team_name}</p>
      <p><strong>Team Leader:</strong> {leader_name}</p>
      <p><strong>Branch:</strong> {branch}</p>
      <p><strong>Total Failures:</strong> {total_failures}</p>
      <p><strong>Fixes Applied:</strong> {fixes_applied}</p>
      <p><strong>Time Taken:</strong> {time_taken}</p>

      <div>
        <span
          className={`px-3 py-1 rounded-full text-white text-sm ${
            status === "PASSED"
              ? "bg-green-500"
              : "bg-red-500"
          }`}
        >
          {status}
        </span>
      </div>
    </div>
  );
}