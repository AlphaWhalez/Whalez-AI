import React, { useEffect, useState } from "react";
import { SafeAreaView, View, Text, ScrollView, TextInput, Button } from "react-native";
import axios from "axios";

export default function App() {
  const [logs, setLogs] = useState([]);
  const [command, setCommand] = useState("");
  const [response, setResponse] = useState("");

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  async function fetchLogs() {
    try {
      const res = await axios.get("http://localhost:5050/api/health");
      setLogs(res.data.recent_logs || []);
    } catch (e) {
      console.error(e);
    }
  }

  async function sendCommand() {
    try {
      const res = await axios.post("http://localhost:5050/api/command", { command });
      setResponse(res.data.result || "Executed");
      setCommand("");
    } catch (e) {
      setResponse("Error sending command");
    }
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#0b1120" }}>
      <ScrollView style={{ padding: 16 }}>
        <Text style={{ fontSize: 24, color: "#22d3ee", marginBottom: 8 }}>
          🐋 Whalez-AI Mobile Mirror
        </Text>

        <Text style={{ color: "white", marginBottom: 6 }}>Runtime Status:</Text>
        {logs.map((log, i) => (
          <View
            key={i}
            style={{ borderBottomColor: "#1f2937", borderBottomWidth: 1, marginBottom: 6 }}
          >
            <Text style={{ color: "#93c5fd" }}>
              {log.status} — {log.metrics?.cpu_percent}% CPU
            </Text>
          </View>
        ))}

        <View style={{ marginTop: 20 }}>
          <Text style={{ color: "#a5f3fc" }}>Send Command:</Text>
          <TextInput
            value={command}
            onChangeText={setCommand}
            placeholder="Type intent..."
            placeholderTextColor="#6b7280"
            style={{
              borderColor: "#22d3ee",
              borderWidth: 1,
              marginVertical: 8,
              color: "white",
              padding: 8
            }}
          />
          <Button title="Execute" onPress={sendCommand} />
          <Text style={{ color: "#22c55e", marginTop: 8 }}>{response}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
