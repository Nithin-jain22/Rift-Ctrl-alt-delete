import { useState } from "react";
import { useAgent } from "../context/AgentContext";

export default function InputSection() {
  const { runAgent, loading } = useAgent();

  const [githubUrl, setGithubUrl] = useState("");
  const [teamName, setTeamName] = useState("");
  const [leaderName, setLeaderName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!githubUrl || !teamName || !leaderName) return;

    runAgent({ githubUrl, teamName, leaderName });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-xl shadow-md space-y-4"
    >
      <h2 className="text-xl font-semibold text-gray-700">
        Run Autonomous Agent
      </h2>

      <input
        type="text"
        placeholder="GitHub Repository URL"
        value={githubUrl}
        onChange={(e) => setGithubUrl(e.target.value)}
        className="w-full border rounded-lg p-3"
      />

      <input
        type="text"
        placeholder="Team Name"
        value={teamName}
        onChange={(e) => setTeamName(e.target.value)}
        className="w-full border rounded-lg p-3"
      />

      <input
        type="text"
        placeholder="Team Leader Name"
        value={leaderName}
        onChange={(e) => setLeaderName(e.target.value)}
        className="w-full border rounded-lg p-3"
      />

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white p-3 rounded-lg font-semibold hover:bg-blue-700 transition"
      >
        {loading ? "Running..." : "Run Agent"}
      </button>
    </form>
  );
}