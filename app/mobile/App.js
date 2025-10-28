import React, { useState, useEffect, useCallback } from "react";
import { View, Text, ScrollView, RefreshControl, ActivityIndicator } from "react-native";
import axios from "axios";

// ⚠️ Set to your PC's Wi-Fi IPv4 (ipconfig) — KEEP PORT 5050 (backend)
const BASE_URL = "http://192.168.103.173:5050";

export default function App() {
  const [health, setHealth] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHealth = useCallback(async () => {
    try {
      const { data } = await axios.get(`${BASE_URL}/api/health`);
      setHealth(data);
    } catch (e) {
      console.log("⚠️ Backend not reachable:", e.message);
      setHealth(null);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const id = setInterval(fetchHealth, 10000);
    return () => clearInterval(id);
  }, [fetchHealth]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchHealth();
    setRefreshing(false);
  }, [fetchHealth]);

  const theme = { bg: "#0b1120", accent: "#22d3ee", text: "#fff", sub: "#a5f3fc" };

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg, padding: 16, paddingTop: 60 }}>
      <Text style={{ color: theme.accent, fontSize: 22, fontWeight: "700", textAlign: "center" }}>
        🐋 Whalez-AI Mobile Mirror
      </Text>

      <View style={{ alignItems: "center", marginTop: 16 }}>
        {health ? (
          <>
            <Text style={{ color: theme.text, fontSize: 16 }}>✅ {health.status}</Text>
            <Text style={{ color: theme.sub, marginTop: 6 }}>
              CPU: {health.metrics.cpu_percent}% • MEM: {health.metrics.memory_mb} MB • Host:{" "}
              {health.metrics.hostname ?? "local"}
            </Text>
          </>
        ) : (
          <ActivityIndicator size="large" color={theme.accent} style={{ marginTop: 24 }} />
        )}
      </View>

      <ScrollView
        style={{ marginTop: 24 }}
        refreshControl={<RefreshControl tintColor={theme.accent} refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={{ borderColor: theme.accent, borderWidth: 1, borderRadius: 12, padding: 12 }}>
          <Text style={{ color: theme.sub, fontWeight: "600", marginBottom: 6, textAlign: "center" }}>
            Agents (open on web)
          </Text>
          <Text style={{ color: theme.text, opacity: 0.85, textAlign: "center" }}>
            Visit {BASE_URL.replace("http://", "")}/api/agents/status
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

Expo’s Metro will still show 8081 (that’s the bundler). Your backend stays on 5050. That’s correct.

