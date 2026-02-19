import InputSection from "../components/InputSection";
import RunSummaryCard from "../components/RunSummaryCard";
import ScorePanel from "../components/ScorePanel";
import FixesTable from "../components/FixesTable";
import Timeline from "../components/Timeline";
import { useAgent } from "../context/AgentContext";

export default function Dashboard() {
  const { loading, error, result } = useAgent();

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4 md:px-8">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Title */}
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800">
            Autonomous DevOps Agent
          </h1>
          <p className="text-gray-500 mt-1">
            CI/CD Failure Detection & Autonomous Fixing System
          </p>
        </div>

        {/* Input Section */}
        <InputSection />

        {/* Loading */}
        {loading && (
          <div className="p-4 bg-blue-100 text-blue-700 rounded-lg animate-pulse">
            Agent is running... Please wait.
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Only show results if available */}
        {result && result.status === "completed" && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <RunSummaryCard data={result} />
              <ScorePanel data={result} />
            </div>

            <FixesTable fixes={result.fixes || []} />

            <Timeline timeline={result.timeline || []} />
          </>
        )}
      </div>
    </div>
  );
}