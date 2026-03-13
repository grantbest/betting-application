'use client';

import { useState, useEffect } from 'react';
import { 
  Activity, 
  Trophy, 
  CheckCircle, 
  XCircle, 
  Clock,
  Database,
  ShieldAlert,
  ShieldCheck,
  Settings,
  ExternalLink,
  Cpu,
  BrainCircuit,
  MessageSquare,
  ChevronRight
} from 'lucide-react';
import Link from 'next/link';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';

interface Bet {
  bet_id: number;
  game_id: number;
  game_info?: string;
  system_triggered: string;
  odds_taken: number;
  stake: number;
  result: string;
  ai_insight?: string;
  created_at: string;
}

interface InningLog {
  log_id: number;
  game_id: number;
  inning_number: number;
  half: string;
  runs_scored: number;
  baserunners: number;
  game_info?: string;
}

interface Team {
  team_id: number;
  abbreviation: string;
  bullpen_era_rank: number;
}

interface AppConfig {
  appEnv: string;
  devUrl: string;
  prodUrl: string;
  discordChannelUrl: string;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'bets' | 'feed' | 'teams' | 'ai'>('bets');
  const [bets, setBets] = useState<Bet[]>([]);
  const [logs, setLogs] = useState<InningLog[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [testLoading, setTestLoading] = useState(false);

  const fetchAiAnalysis = async () => {
    setAiLoading(true);
    try {
      const res = await fetch('/api/ai/optimize');
      const data = await res.json();
      setAiAnalysis(data.analysis);
    } catch (err) {
      console.error('AI Fetch failed', err);
    } finally {
      setAiLoading(false);
    }
  };

  const fetchData = async () => {
    try {
      const [betsRes, logsRes, teamsRes, configRes] = await Promise.all([
        fetch('/api/bets'),
        fetch('/api/logs'),
        fetch('/api/teams'),
        fetch('/api/config')
      ]);
      setBets(await betsRes.json());
      setLogs(await logsRes.json());
      setTeams(await teamsRes.json());
      setConfig(await configRes.json());
    } catch (err) {
      console.error('Failed to fetch data', err);
    } finally {
      setLoading(false);
    }
  };

  const sendTestAlert = async () => {
    setTestLoading(true);
    try {
      const res = await fetch('/api/test-discord', { method: 'POST' });
      const data = await res.json();
      if (data.error) alert(data.error);
      else alert('Test Alert Sent!');
    } catch (err) {
      alert('Network error');
    } finally {
      setTestLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const updateResult = async (bet_id: number, result: string) => {
    try {
      await fetch('/api/bets', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bet_id, result }),
      });
      fetchData();
    } catch (err) {
      console.error('Update failed', err);
    }
  };

  const stats = {
    total: bets.length,
    wins: bets.filter(b => b.result === 'WON').length,
    losses: bets.filter(b => b.result === 'LOST').length,
    pending: bets.filter(b => b.result === 'PENDING').length,
    winRate: bets.filter(b => b.result !== 'PENDING').length > 0
      ? (bets.filter(b => b.result === 'WON').length / bets.filter(b => b.result !== 'PENDING').length * 100).toFixed(1)
      : '0.0'
  };

  const chartData = [
    { name: 'NR2I Regression', wins: bets.filter(b => b.system_triggered === 'NR2I Regression' && b.result === 'WON').length },
    { name: 'Big Inning Momentum', wins: bets.filter(b => b.system_triggered === 'Big Inning Momentum' && b.result === 'WON').length },
  ];

  const currentEnv = config?.appEnv || 'development';
  const isProd = currentEnv === 'production';
  const switchUrl = isProd ? config?.devUrl : config?.prodUrl;

  if (!config) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">Loading Configuration...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-4 md:p-6 font-sans">
      <div className="max-w-7xl mx-auto space-y-6 md:y-8">
        
        {/* Header */}
        <header className="flex flex-col lg:flex-row lg:justify-between lg:items-center border-b border-slate-800 pb-6 gap-6">
          <div className="flex flex-col">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight">BestFam Live Dashboard</h1>
              <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest border ${
                isProd ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {currentEnv}
              </span>
            </div>
            <p className="text-slate-400 mt-1 text-sm md:text-base">Real-time management & analytics dashboard.</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3 md:gap-4">
            <a 
              href={switchUrl}
              className="text-xs text-slate-500 hover:text-blue-400 transition-colors flex items-center gap-1 border border-slate-800 px-3 py-2 rounded-lg hover:border-blue-500/30"
            >
              <Activity size={12} /> <span className="hidden sm:inline">Switch to</span> {isProd ? 'Dev' : 'Production'}
            </a>
            <Link 
              href="/admin"
              className="bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2"
            >
              <ShieldCheck size={16} className="text-blue-400" /> <span className="hidden sm:inline">Admin</span>
            </Link>
            <Link 
              href="/rules"
              className="bg-blue-600/10 border border-blue-500/20 hover:bg-blue-600/20 text-blue-400 px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2"
            >
              <Settings size={16} /> <span className="hidden sm:inline">Rules Engine</span>
            </Link>
            <div className="flex flex-col gap-1">
              <button 
                onClick={sendTestAlert}
                disabled={testLoading}
                className="bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 px-4 py-2 rounded-lg text-sm transition-all disabled:opacity-50 min-h-[40px]"
              >
                {testLoading ? 'Sending...' : 'Test Discord Alert'}
              </button>
              <a 
                href={config.discordChannelUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] text-slate-500 hover:text-indigo-400 transition-colors flex items-center justify-center gap-1 py-1"
              >
                <ExternalLink size={10} /> View Discord Channel
              </a>
            </div>
            <div className="flex items-center gap-2 bg-slate-900 px-4 py-2 rounded-full border border-emerald-500/30">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-emerald-400">Engine Online</span>
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          <StatCard title="Opportunities" value={stats.total} icon={<Activity className="text-blue-400" />} />
          <StatCard title="Win Rate" value={`${stats.winRate}%`} icon={<Trophy className="text-yellow-400" />} />
          <StatCard title="Total Wins" value={stats.wins} icon={<CheckCircle className="text-emerald-400" />} />
          <StatCard title="Pending" value={stats.pending} icon={<Clock className="text-slate-400" />} />
        </div>

        {/* Tabs Switcher - Scrollable on mobile */}
        <div className="overflow-x-auto pb-2 scrollbar-hide">
          <div className="flex gap-1 bg-slate-900/80 p-1 rounded-xl w-max md:w-fit border border-slate-800">
            <TabButton active={activeTab === 'bets'} onClick={() => setActiveTab('bets')} icon={<Trophy size={16} />} label="Bet History" />
            <TabButton active={activeTab === 'feed'} onClick={() => setActiveTab('feed')} icon={<Database size={16} />} label="Live Feed" />
            <TabButton active={activeTab === 'teams'} onClick={() => setActiveTab('teams')} icon={<ShieldAlert size={16} />} label="Teams" />
            <TabButton active={activeTab === 'ai'} onClick={() => setActiveTab('ai')} icon={<Cpu size={16} />} label="AI Lab" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            
            {/* BET HISTORY TAB */}
            {activeTab === 'bets' && (
              <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
                <div className="p-4 md:p-6 border-b border-slate-800 flex justify-between items-center">
                  <h2 className="text-lg md:text-xl font-semibold">Opportunities Tracked</h2>
                </div>
                
                {/* Desktop Table View */}
                <div className="hidden lg:block overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="text-xs uppercase text-slate-500 bg-slate-950/50">
                      <tr>
                        <th className="px-6 py-4">Game</th>
                        <th className="px-6 py-4">System</th>
                        <th className="px-6 py-4">Stake</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4 text-center">AI</th>
                        <th className="px-6 py-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {loading ? (
                        <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-500">Loading...</td></tr>
                      ) : bets.length === 0 ? (
                        <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-500">No data.</td></tr>
                      ) : (
                        bets.map((bet) => (
                          <tr key={bet.bet_id} className="hover:bg-slate-800/30 transition-colors group">
                            <td className="px-6 py-4 text-xs font-bold text-slate-300">{bet.game_info || `ID: ${bet.game_id}`}</td>
                            <td className="px-6 py-4 text-sm font-medium">{bet.system_triggered}</td>
                            <td className="px-6 py-4 text-sm">{(bet.stake * 100).toFixed(1)}%</td>
                            <td className="px-6 py-4">
                              <StatusBadge status={bet.result} />
                            </td>
                            <td className="px-6 py-4 text-center">
                              {bet.ai_insight ? (
                                <div className="relative group/insight inline-block">
                                  <BrainCircuit size={18} className="text-indigo-400 cursor-help mx-auto" />
                                  <div className="absolute right-0 bottom-full mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-xl opacity-0 group-hover/insight:opacity-100 transition-opacity pointer-events-none z-50 text-[10px] leading-relaxed text-slate-300 italic text-left">
                                    {bet.ai_insight}
                                  </div>
                                </div>
                              ) : <span className="text-slate-700">-</span>}
                            </td>
                            <td className="px-6 py-4">
                              {bet.result === 'PENDING' && (
                                <div className="flex gap-2">
                                  <button onClick={() => updateResult(bet.bet_id, 'WON')} className="p-1 hover:text-emerald-400 transition-colors">
                                    <CheckCircle size={18} />
                                  </button>
                                  <button onClick={() => updateResult(bet.bet_id, 'LOST')} className="p-1 hover:text-rose-400 transition-colors">
                                    <XCircle size={18} />
                                  </button>
                                </div>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Mobile Card View */}
                <div className="lg:hidden divide-y divide-slate-800">
                  {loading ? (
                    <div className="p-8 text-center text-slate-500">Loading...</div>
                  ) : bets.map((bet) => (
                    <div key={bet.bet_id} className="p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Game</p>
                          <p className="text-xs font-bold text-slate-200">{bet.game_info || `ID: ${bet.game_id}`}</p>
                        </div>
                        <StatusBadge status={bet.result} />
                      </div>
                      <div className="flex justify-between items-end">
                        <div>
                          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">System</p>
                          <p className="text-sm font-medium">{bet.system_triggered}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Stake</p>
                          <p className="text-sm">{(bet.stake * 100).toFixed(1)}%</p>
                        </div>
                      </div>
                      {bet.ai_insight && (
                        <div className="bg-indigo-500/5 border border-indigo-500/10 p-3 rounded-lg flex gap-2">
                          <BrainCircuit size={14} className="text-indigo-400 shrink-0 mt-0.5" />
                          <p className="text-[10px] text-slate-400 leading-relaxed italic">{bet.ai_insight}</p>
                        </div>
                      )}
                      {bet.result === 'PENDING' && (
                        <div className="flex gap-2 pt-2">
                          <button onClick={() => updateResult(bet.bet_id, 'WON')} className="flex-1 bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1">
                            <CheckCircle size={14} /> WON
                          </button>
                          <button onClick={() => updateResult(bet.bet_id, 'LOST')} className="flex-1 bg-rose-600/10 border border-rose-500/20 text-rose-400 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1">
                            <XCircle size={14} /> LOST
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* LIVE FEED TAB */}
            {activeTab === 'feed' && (
              <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
                <div className="p-4 md:p-6 border-b border-slate-800">
                  <h2 className="text-lg md:text-xl font-semibold">Live Inning Logs</h2>
                </div>
                
                {/* Desktop Feed Table */}
                <div className="hidden md:block overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="text-xs uppercase text-slate-500 bg-slate-950/50">
                      <tr>
                        <th className="px-6 py-4">Game</th>
                        <th className="px-6 py-4 text-center">Inning</th>
                        <th className="px-6 py-4">Half</th>
                        <th className="px-6 py-4 text-emerald-400">Runs</th>
                        <th className="px-6 py-4 text-blue-400">Runners</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 font-mono text-sm">
                      {logs.map((log) => (
                        <tr key={log.log_id} className="hover:bg-slate-800/30 transition-colors text-[11px]">
                          <td className="px-6 py-3 text-slate-300 font-bold whitespace-nowrap">{log.game_info || `ID: ${log.game_id}`}</td>
                          <td className="px-6 py-3 text-center">{log.inning_number}</td>
                          <td className="px-6 py-3 uppercase">{log.half}</td>
                          <td className="px-6 py-3 text-emerald-400 font-bold">{log.runs_scored}</td>
                          <td className="px-6 py-3 text-blue-400">{log.baserunners}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Mobile Feed Cards */}
                <div className="md:hidden divide-y divide-slate-800">
                  {logs.map((log) => (
                    <div key={log.log_id} className="p-4 space-y-2 bg-slate-950/20">
                      <div className="text-[10px] font-black text-slate-400 uppercase tracking-tighter border-b border-slate-800 pb-1">
                        {log.game_info || `Game ID: ${log.game_id}`}
                      </div>
                      <div className="flex justify-between items-center">
                        <div className="flex items-baseline gap-2">
                          <span className="text-lg font-bold">{log.inning_number}</span>
                          <span className="text-[10px] text-slate-500 uppercase font-black">{log.half}</span>
                        </div>
                        <div className="flex gap-4">
                          <div className="text-center">
                            <p className="text-[8px] text-slate-500 uppercase">Runs</p>
                            <p className="text-emerald-400 font-mono font-bold">{log.runs_scored}</p>
                          </div>
                          <div className="text-center">
                            <p className="text-[8px] text-slate-500 uppercase">Runners</p>
                            <p className="text-blue-400 font-mono font-bold">{log.baserunners}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TEAMS TAB */}
            {activeTab === 'teams' && (
              <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
                <div className="p-4 md:p-6 border-b border-slate-800">
                  <h2 className="text-lg md:text-xl font-semibold">Bullpen Rankings</h2>
                </div>
                <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-px bg-slate-800">
                  {teams.map((team) => (
                    <div key={team.team_id} className="bg-slate-950 p-3 md:p-4 flex flex-col items-center gap-1">
                      <span className="text-xl md:text-2xl font-black text-slate-700">#{team.bullpen_era_rank}</span>
                      <span className="text-md md:text-lg font-bold text-white">{team.abbreviation}</span>
                      <div className={`h-1 w-full rounded-full mt-2 ${team.bullpen_era_rank <= 10 ? 'bg-emerald-500' : team.bullpen_era_rank <= 20 ? 'bg-yellow-500' : 'bg-rose-500'}`} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI LAB TAB */}
            {activeTab === 'ai' && (
              <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden flex flex-col min-h-[400px]">
                <div className="p-4 md:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:justify-between sm:items-center bg-indigo-500/5 gap-4">
                  <div>
                    <h2 className="text-lg md:text-xl font-semibold flex items-center gap-2">
                      <Cpu className="text-indigo-400" size={20} /> AI Strategy Lab
                    </h2>
                    <p className="text-xs text-slate-500 mt-1">Direct analysis from local Ollama (llama3).</p>
                  </div>
                  <button 
                    onClick={fetchAiAnalysis}
                    disabled={aiLoading}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-3 rounded-lg text-sm font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2 w-full sm:w-auto"
                  >
                    {aiLoading ? <Activity size={16} className="animate-spin" /> : <BrainCircuit size={16} />}
                    {aiLoading ? 'Analyzing...' : 'Run Strategy Audit'}
                  </button>
                </div>
                
                <div className="p-4 md:p-8 flex-1">
                  {aiLoading ? (
                    <div className="flex flex-col items-center justify-center h-full space-y-4 py-12">
                      <Cpu size={48} className="text-indigo-500/20 animate-pulse" />
                      <p className="text-indigo-300 font-medium animate-pulse text-center">Consulting Local LLM...</p>
                    </div>
                  ) : aiAnalysis ? (
                    <div className="prose prose-invert max-w-none">
                      <div className="bg-slate-950/50 border border-slate-800 p-4 md:p-6 rounded-xl shadow-inner whitespace-pre-wrap font-sans text-xs md:text-sm leading-relaxed text-slate-300">
                        {aiAnalysis}
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full py-12 text-center space-y-4">
                      <Cpu size={32} className="text-slate-700" />
                      <p className="text-slate-400 font-medium">Ready for Strategy Audit</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Analytics Column - Hidden on mobile if not focused */}
          <div className="space-y-6 md:y-8">
            <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 md:p-6">
              <h2 className="text-lg md:text-xl font-semibold mb-6">Wins by System</h2>
              <div className="h-48 md:h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={8} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                      itemStyle={{ color: '#94a3b8', fontSize: '10px' }}
                    />
                    <Bar dataKey="wins">
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#3b82f6' : '#8b5cf6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600/20 to-emerald-600/20 rounded-xl border border-blue-500/20 p-4 md:p-6">
              <h3 className="text-md font-semibold text-blue-300">Live Strategy Context</h3>
              <p className="text-slate-400 text-xs md:text-sm mt-2 leading-relaxed italic">
                Scanning {logs.length} data points. 
                {teams.length > 0 && ` Favoring matchups against ${teams[teams.length-1].abbreviation} (Rank ${teams[teams.length-1].bullpen_era_rank}).`}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon }: { title: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="bg-slate-900/50 p-4 md:p-6 rounded-xl border border-slate-800 flex flex-col gap-1 md:gap-2">
      <div className="flex justify-between items-start">
        <span className="text-slate-500 text-[10px] md:text-sm font-bold uppercase tracking-wider">{title}</span>
        <div className="scale-75 md:scale-100 opacity-50 md:opacity-100">{icon}</div>
      </div>
      <span className="text-xl md:text-3xl font-black tracking-tight">{value}</span>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-3 md:py-2 rounded-lg text-xs md:text-sm font-bold transition-all whitespace-nowrap ${
        active 
          ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
          : 'text-slate-500 hover:text-slate-200 hover:bg-slate-800'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    WON: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    LOST: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    PENDING: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  };
  return (
    <span className={`px-2 py-1 rounded text-[9px] md:text-[10px] font-black border tracking-tighter ${styles[status]}`}>
      {status}
    </span>
  );
}
