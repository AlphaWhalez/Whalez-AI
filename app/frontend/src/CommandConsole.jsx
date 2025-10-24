import React, { useState } from "react";
import axios from "axios";

export default function CommandConsole() {
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState("");

  const sendCommand = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;
    try {
      const res = await axios.post("/api/command", { command });
      setOutput(res.data.result);
      setCommand("");
    } catch (err) {
      setOutput("❌ Failed to send command.");
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow mt-6">
      <h2 className="text-xl mb-3">Command Interface Console</h2>
      <form onSubmit={sendCommand} className="flex gap-2">
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Enter a command..."
          className="flex-1 px-3 py-2 rounded bg-gray-700 text-white focus:outline-none"
        />
        <button
          type="submit"
          className="bg-green-500 hover:bg-green-600 text-black font-bold px-4 py-2 rounded"
        >
          Send
        </button>
      </form>
      {output && (
        <div className="mt-4 text-sm text-gray-300 bg-gray-900 p-3 rounded border border-gray-700">
          <p>{output}</p>
        </div>
      )}
    </div>
  );
}
