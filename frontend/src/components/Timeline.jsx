import { useAgent } from "../context/AgentContext";

export default function Timeline() {
  const { timeline, retryLimit } = useAgent();

  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="bg-white p-6 rounded-xl shadow-md space-y-3">
      <h2 className="text-xl font-semibold text-gray-700">
        CI/CD Timeline
      </h2>

      {timeline.map((item, index) => (
        <div
          key={index}
          className="flex justify-between items-center border-b pb-2"
        >
          <span>
            Iteration {item.iteration}
            {retryLimit || item.retry_limit ? ` (${item.iteration}/${retryLimit || item.retry_limit})` : ""}
          </span>

          <span
            className={`px-3 py-1 rounded-full text-white text-sm ${
              item.ci_status === "PASSED"
                ? "bg-green-500"
                : "bg-red-500"
            }`}
          >
            {item.ci_status}
          </span>

          <span className="text-sm text-gray-500">
            {item.timestamp}
          </span>
        </div>
      ))}
    </div>
  );
}