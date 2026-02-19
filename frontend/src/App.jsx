import { AgentProvider } from "./context/AgentContext";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <AgentProvider>
      <Dashboard />
    </AgentProvider>
  );
}

export default App;