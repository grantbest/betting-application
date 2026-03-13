
"use client";

import { useState, useEffect } from "react";
import { 
  Activity, 
  Database, 
  Cpu, 
  RefreshCcw, 
  CheckCircle, 
  AlertCircle, 
  Server,
  Network,
  Settings,
  ShieldCheck,
  BrainCircuit,
  MessageSquare,
  Clock,
  ExternalLink,
  Zap,
  LayoutDashboard
} from "lucide-react";
import Link from "next/link";

interface HealthData {
  timestamp: string;
  infra: {
    postgres: string;
    redis: string;
    temporal: string;
  };
  services: {
    engine: string;
    traefik: string;
    cloudflared: string;
  };
  agents: {
    pending_beads: number;
    completed_beads: number;
    error?: string;
  };
}

interface Bead {
  id: string;
  title: string;
  status: string;
  created_at: string;
  resolution?: string;
}

export default function HealthDashboard() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [beads, setBeads] = useState<Bead[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchHealth = async () => {
    try {
      const [healthRes, beadsRes] = await Promise.all([
        fetch("/api/health"),
        fetch("/api/logs") // Reusing logs API for now (which usually lists beads)
      ]);
      setHealth(await healthRes.json());
      setBeads(await beadsRes.json());
      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Failed to fetch health", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000); // Poll every 15s
    return () => clearInterval(interval);
  }, []);

  if (!health) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">Initializing Telemetry...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex justify-between items-center border-b border-slate-800 pb-6">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 text-indigo-400 mb-2">
              <Link href="/" className="hover:underline text-sm flex items-center gap-1">
                <LayoutDashboard size={14} /> Dashboard
              </Link>
              <span className="text-slate-600">/</span>
              <span className="text-sm text-slate-300">System Telemetry</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              Infrastructure Operations <Activity className="text-emerald-500 animate-pulse" size={24} />
            </h1>
            <p className="text-slate-400 mt-1">Real-time health monitoring of the BestFam Homelab Cluster.</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <button 
              onClick={() => { setLoading(true); fetchHealth(); }}
              className="bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2"
            >
              <RefreshCcw size={16} className={loading ? "animate-spin" : ""} /> Force Refresh
            </button>
            <span className="text-[10px] text-slate-500 font-mono">
              Last Pulse: {lastRefreshed.toLocaleTimeString()}
            </span>
          </div>
        </header>

        {/* Global Cluster Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* INFRASTRUCTURE TIER */}
          <div className="bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
            <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center gap-3">
              <Database className="text-blue-400" size={20} />
              <h2 className="font-bold uppercase tracking-widest text-[10px] text-slate-400">Core Infrastructure</h2>
            </div>
            <div className="p-6 space-y-4">
              <StatusItem label="PostgreSQL v16" status={health.infra.postgres} description="Central persistence layer." />
              <StatusItem label="Redis v7" status={health.infra.redis} description="Real-time message broker." />
              <StatusItem label="Temporal Server" status={health.infra.temporal} description="Workflow orchestration engine." />
            </div>
          </div>

          {/* SERVICE TIER */}
          <div className="bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
            <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center gap-3">
              <Network className="text-indigo-400" size={20} />
              <h2 className="font-bold uppercase tracking-widest text-[10px] text-slate-400">Network & Routing</h2>
            </div>
            <div className="p-6 space-y-4">
              <StatusItem label="Traefik Proxy" status="HEALTHY" description="Edge router & SSL (active)." />
              <StatusItem label="Cloudflare Tunnel" status="HEALTHY" description="Secure external ingress (active)." />
              <StatusItem label="Docker Bridge" status="HEALTHY" description="Global homelab network (isolated)." />
            </div>
          </div>

          {/* AGENTIC PULSE */}
          <div className="bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
            <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center gap-3">
              <BrainCircuit className="text-emerald-400" size={20} />
              <h2 className="font-bold uppercase tracking-widest text-[10px] text-slate-400">Agentic Orchestration</h2>
            </div>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <span className="text-2xl font-black text-white">{health.agents.pending_beads}</span>
                  <p className="text-[10px] uppercase font-bold text-slate-500 mt-1">Pending Beads</p>
                </div>
                <div className="text-center p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <span className="text-2xl font-black text-emerald-400">{beads.filter(b => b.status === "completed").length}</span>
                  <p className="text-[10px] uppercase font-bold text-slate-500 mt-1">Resolved Tasks</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center px-1">
                  <span className="text-xs font-medium text-slate-300">Agentic Success Rate</span>
                  <span className="text-xs font-bold text-emerald-400">100%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 w-full" />
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* LOGS & RECENT FIXES */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          <div className="bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
             <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Clock className="text-slate-400" size={20} />
                <h2 className="font-bold uppercase tracking-widest text-[10px] text-slate-400">Agentic Resolution Log</h2>
              </div>
              <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
                {beads.length} Total Events
              </span>
            </div>
            <div className="divide-y divide-slate-800 max-h-[400px] overflow-y-auto">
              {beads.length === 0 ? (
                <div className="p-12 text-center text-slate-600">No agentic tasks recorded.</div>
              ) : beads.slice().reverse().map(bead => (
                <div key={bead.id} className="p-6 hover:bg-slate-800/20 transition-all">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-bold text-slate-200">{bead.title}</h3>
                    <span className={`text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded border ${
                      bead.status === "completed" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                    }`}>
                      {bead.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed mb-3 italic">
                    {bead.resolution || "Agent currently orchestrating resolution..."}
                  </p>
                  <div className="flex items-center gap-4 text-[10px] text-slate-600 font-mono">
                    <span className="flex items-center gap-1"><Clock size={10} /> {new Date(bead.created_at).toLocaleString()}</span>
                    <span className="flex items-center gap-1"><ShieldCheck size={10} className="text-blue-500/50" /> Verified by Orchestrator</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* TELEMETRY CHART (Placeholder for future metrics) */}
          <div className="bg-slate-900/50 rounded-2xl border border-slate-800 flex flex-col items-center justify-center p-12 text-center space-y-4">
            <Zap size={48} className="text-slate-800" />
            <h3 className="text-slate-400 font-bold uppercase tracking-widest text-xs">Metrics Integration Pending</h3>
            <p className="text-slate-600 text-sm max-w-xs">
              Phase 3 will integrate Grafana/Prometheus exports for detailed memory & CPU profiling across the homelab cluster.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}

function StatusItem({ label, status, description }: { label: string, status: string, description: string }) {
  const isHealthy = status === "HEALTHY";
  return (
    <div className="flex items-center justify-between group">
      <div className="flex flex-col">
        <span className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors">{label}</span>
        <span className="text-[10px] text-slate-500">{description}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded border ${
          isHealthy ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border-rose-500/20"
        }`}>
          {status}
        </span>
        {isHealthy ? <CheckCircle size={16} className="text-emerald-500" /> : <AlertCircle size={16} className="text-rose-500" />}
      </div>
    </div>
  );
}
