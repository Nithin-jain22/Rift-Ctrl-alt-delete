import { useAgent } from "../context/AgentContext";

export default function ScorePanel() {
  const { score } = useAgent();

  if (!score) return null;

  const { base, speed_bonus, efficiency_penalty, final_score } = score;
  const progress = Math.min(Math.max(final_score || 0, 0), 100);

  return (
    <div className="bg-white p-6 rounded-xl shadow-md space-y-2">
      <h2 className="text-xl font-semibold text-gray-700">
        Score Breakdown
      </h2>

      <p>Base Score: {base}</p>
      <p>Speed Bonus: +{speed_bonus}</p>
      <p>Efficiency Penalty: {efficiency_penalty}</p>

      <div className="mt-4 text-3xl font-bold text-blue-600">
        Final Score: {final_score}
      </div>

      <div className="mt-4">
        <div className="h-2 w-full rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-blue-600"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}