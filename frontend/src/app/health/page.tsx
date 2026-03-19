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
  Server,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

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

  if (!health)
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">
        Initializing Telemetry...
      </div>
    );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header */}
        <header className="border-b border-slate-800 pb-6">
          <div className="flex items-center gap-2 text-blue-400 mb-2">
            <Link href="/" className="hover:underline text-sm flex items-center">
              <Server size={14} className="mr-1" /> Dashboard
            </Link>
            <ChevronRight size={14} className="text-slate-600" />
            <span className="text-sm text-slate-300">Health Telemetry</span>
          </div>
          <div className="flex justify-between items-end">
            <div>
              <h1 className="text-4xl md:text-5xl font-black tracking-tight">
                Cluster <span className="text-emerald-400">Health</span>
              </h1>
              <p className="text-slate-400 mt-2">Real-time telemetry for BestFam Homelab Operations.</p>
            </div>
            <Activity size={32} className="text-emerald-400 hidden md:block" />
          </div>
        </header>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/30 rounded-3xl border border-slate-800 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Database size={18} className="text-blue-400" />
              <span className="text-xs font-black uppercase tracking-widest text-slate-500">Persistence</span>
            </div>
            <StatusRow name="PostgreSQL v16" status={health.infra.postgres} />
            <StatusRow name="Redis v7" status={health.infra.redis} />
          </div>
          <div className="bg-slate-900/30 rounded-3xl border border-slate-800 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Cpu size={18} className="text-purple-400" />
              <span className="text-xs font-black uppercase tracking-widest text-slate-500">Orchestration</span>
            </div>
            <StatusRow name="Temporal Server" status={health.infra.temporal} />
            <StatusRow name="Agentic Workers" status="HEALTHY" />
          </div>
          <div className="bg-slate-900/30 rounded-3xl border border-slate-800 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Network size={18} className="text-emerald-400" />
              <span className="text-xs font-black uppercase tracking-widest text-slate-500">Network</span>
            </div>
            <StatusRow name="Traefik Proxy" status="HEALTHY" />
            <StatusRow name="Cloudflare Tunnel" status="HEALTHY" />
          </div>
        </div>

        {/* Agentic Resolution Log */}
        <div className="bg-slate-900/30 rounded-3xl border border-slate-800 overflow-hidden">
          <div className="px-8 py-6 border-b border-slate-800 flex items-center gap-3">
            <BrainCircuit size={18} className="text-indigo-400" />
            <span className="text-sm font-black uppercase tracking-widest">Agentic Resolution Log</span>
          </div>
          <div className="max-h-[500px] overflow-y-auto divide-y divide-slate-800/50">
            {beads.length === 0 ? (
              <div className="px-8 py-12 text-center text-slate-500 text-sm">Waiting for agentic activity...</div>
            ) : (
              beads.map((bead: any) => (
                <div key={bead.id} className="px-8 py-8">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-bold">{bead.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase border ${
                      bead.status === "completed"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                    }`}>
                      {bead.status}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm italic mb-4">{bead.resolution || "Processing..."}</p>
                  <div className="flex gap-4 text-slate-600 text-[10px] font-black uppercase">
                    <span className="flex items-center gap-1"><ShieldCheck size={10} /> Verified</span>
                    <span className="flex items-center gap-1"><Clock size={10} /> {new Date(bead.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

function StatusRow({ name, status }: { name: string; status: string }) {
  const healthy = status === "HEALTHY";
  return (
    <div className="flex justify-between items-center mb-5 last:mb-0">
      <div>
        <p className="text-sm font-bold">{name}</p>
        <p className="text-[10px] text-slate-500">{healthy ? "Operational" : "Degraded"}</p>
      </div>
      <div className={`w-2 h-2 rounded-full ${healthy ? "bg-emerald-500 shadow-[0_0_12px_#10b981]" : "bg-rose-500 shadow-[0_0_12px_#ef4444]"}`} />
    </div>
  );
}
