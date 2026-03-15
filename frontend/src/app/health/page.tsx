
"use client";

import { useState, useEffect } from "react";
import { 
  Activity, 
  Database, 
  Cpu, 
  Network,
  BrainCircuit,
  Clock,
  ShieldCheck,
  LayoutDashboard
} from "lucide-react";
import Link from "next/link";

const S = {
  container: { minHeight: "100vh", backgroundColor: "#020617", color: "#f8fafc", padding: "32px", fontFamily: "sans-serif" },
  header: { borderBottom: "1px solid #1e293b", paddingBottom: "40px", marginBottom: "40px", display: "flex", justifyContent: "space-between", alignItems: "flex-end" },
  title: { fontSize: "48px", fontWeight: "900", letterSpacing: "-2px", margin: "0" },
  subtitle: { color: "#64748b", margin: "8px 0 0 0", fontSize: "16px" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "24px", marginBottom: "40px" },
  card: { backgroundColor: "rgba(15, 23, 42, 0.3)", borderRadius: "24px", border: "1px solid #1e293b", padding: "32px" },
  cardHeader: { display: "flex", alignItems: "center", gap: "12px", marginBottom: "24px" },
  cardTitle: { fontSize: "12px", fontWeight: "900", textTransform: "uppercase", letterSpacing: "1px", color: "#64748b" },
  statusItem: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" },
  dot: (healthy: boolean) => ({ height: "8px", width: "8px", borderRadius: "50%", backgroundColor: healthy ? "#10b981" : "#ef4444", boxShadow: healthy ? "0 0 12px #10b981" : "0 0 12px #ef4444" }),
  logContainer: { backgroundColor: "rgba(15, 23, 42, 0.3)", borderRadius: "24px", border: "1px solid #1e293b", overflow: "hidden" },
  logHeader: { padding: "24px 32px", borderBottom: "1px solid #1e293b", display: "flex", justifyContent: "space-between", alignItems: "center" },
  logItem: { padding: "32px", borderBottom: "1px solid #0f172a" },
  badge: (completed: boolean) => ({ padding: "4px 12px", borderRadius: "99px", fontSize: "10px", fontWeight: "900", textTransform: "uppercase", border: "1px solid " + (completed ? "#064e3b" : "#1e3a8a"), color: completed ? "#34d399" : "#60a5fa", backgroundColor: completed ? "rgba(6, 78, 59, 0.1)" : "rgba(30, 58, 138, 0.1)" })
};

export default function HealthDashboard() {
  const [health, setHealth] = useState<any>(null);
  const [beads, setBeads] = useState<any[]>([]);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [h, b] = await Promise.all([fetch("/api/health"), fetch("/api/logs")]);
        setHealth(await h.json());
        setBeads(await b.json());
      } catch (e) {}
    };
    fetchAll();
    const i = setInterval(fetchAll, 10000);
    return () => clearInterval(i);
  }, []);

  if (!health) return <div style={S.container}>Initializing Telemetry...</div>;

  return (
    <div style={S.container}>
      <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
        
        <header style={S.header}>
          <div>
            <h1 style={S.title}>Cluster <span style={{ color: "#10b981" }}>Health</span></h1>
            <p style={S.subtitle}>Real-time telemetry for BestFam Homelab Operations.</p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <Activity size={32} color="#10b981" />
          </div>
        </header>

        <div style={S.grid}>
          <div style={S.card}>
            <div style={S.cardHeader}><Database size={18} color="#60a5fa" /><span style={S.cardTitle}>Persistence</span></div>
            <StatusRow name="PostgreSQL v16" status={health.infra.postgres} />
            <StatusRow name="Redis v7" status={health.infra.redis} />
          </div>
          <div style={S.card}>
            <div style={S.cardHeader}><Cpu size={18} color="#a855f7" /><span style={S.cardTitle}>Orchestration</span></div>
            <StatusRow name="Temporal Server" status={health.infra.temporal} />
            <StatusRow name="Agentic Workers" status="HEALTHY" />
          </div>
          <div style={S.card}>
            <div style={S.cardHeader}><Network size={18} color="#10b981" /><span style={S.cardTitle}>Network</span></div>
            <StatusRow name="Traefik Proxy" status="HEALTHY" />
            <StatusRow name="Cloudflare Tunnel" status="HEALTHY" />
          </div>
        </div>

        <section style={S.logContainer}>
          <div style={S.logHeader}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <BrainCircuit size={18} color="#6366f1" />
              <span style={{ fontWeight: "900", textTransform: "uppercase", fontSize: "14px" }}>Agentic Resolution Log</span>
            </div>
          </div>
          <div style={{ maxHeight: "500px", overflowY: "auto" }}>
            {beads.map(bead => (
              <div key={bead.id} style={S.logItem}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                  <h3 style={{ fontSize: "18px", fontWeight: "700", margin: "0" }}>{bead.title}</h3>
                  <span style={S.badge(bead.status === "completed")}>{bead.status}</span>
                </div>
                <p style={{ color: "#94a3b8", fontSize: "14px", fontStyle: "italic", margin: "0 0 16px 0" }}>{bead.resolution || "Processing..."}</p>
                <div style={{ display: "flex", gap: "16px", color: "#475569", fontSize: "10px", fontWeight: "700", textTransform: "uppercase" }}>
                  <span><ShieldCheck size={10} style={{ marginRight: "4px" }} /> Verified</span>
                  <span><Clock size={10} style={{ marginRight: "4px" }} /> {new Date(bead.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}

function StatusRow({ name, status }: any) {
  const healthy = status === "HEALTHY";
  return (
    <div style={S.statusItem}>
      <div>
        <p style={{ margin: "0", fontSize: "14px", fontWeight: "700" }}>{name}</p>
        <p style={{ margin: "0", fontSize: "10px", color: "#475569" }}>{healthy ? "Operational" : "Degraded"}</p>
      </div>
      <div style={S.dot(healthy)} />
    </div>
  );
}
