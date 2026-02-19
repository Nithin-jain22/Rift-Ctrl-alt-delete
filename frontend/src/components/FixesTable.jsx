import { useAgent } from "../context/AgentContext";

export default function FixesTable() {
  const { fixes } = useAgent();

  if (!fixes || fixes.length === 0) return null;

  return (
    <div className="bg-white p-6 rounded-xl shadow-md overflow-x-auto">
      <h2 className="text-xl font-semibold text-gray-700 mb-4">
        Fixes Applied
      </h2>

      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b">
            <th className="p-2">File</th>
            <th className="p-2">Bug Type</th>
            <th className="p-2">Line</th>
            <th className="p-2">Commit</th>
            <th className="p-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {fixes.map((fix, index) => (
            <tr key={index} className="border-b">
              <td className="p-2">{fix.file}</td>
              <td className="p-2">{fix.bug_type}</td>
              <td className="p-2">{fix.line}</td>
              <td className="p-2">{fix.commit_message}</td>
              <td
                className={`p-2 font-semibold ${
                  fix.status === "Fixed"
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {fix.status === "Fixed" ? "✓ Fixed" : "✗ Failed"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}