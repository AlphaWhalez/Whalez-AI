
import DeployCard from "./components/DeployCard";
import SecurityStatus from "./components/SecurityStatus";

export default function App() {
  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Whalez-AI • Governance Console</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <SecurityStatus />
        <DeployCard />
      </div>
    </div>
  );
}
