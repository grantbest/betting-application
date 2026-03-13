'use client';

import { useState, useEffect } from 'react';
import { Settings, Save, ShieldCheck, AlertCircle, Server, ChevronRight, Activity } from 'lucide-react';
import Link from 'next/link';

interface SystemSetting {
  setting_key: string;
  setting_value: string;
  updated_at: string;
}

interface AppConfig {
  appEnv: string;
  devUrl: string;
  prodUrl: string;
}

export default function AdminSettings() {
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const fetchData = async () => {
    try {
      const [settingsRes, configRes] = await Promise.all([
        fetch('/api/settings'),
        fetch('/api/config')
      ]);
      setSettings(await settingsRes.json());
      setConfig(await configRes.json());
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const updateSetting = (key: string, value: string) => {
    setSettings(settings.map(s => s.setting_key === key ? { ...s, setting_value: value } : s));
  };

  const saveSettings = async () => {
    setSaving(true);
    setMessage(null);
    try {
      for (const setting of settings) {
        await fetch('/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(setting)
        });
      }
      setMessage({ type: 'success', text: 'System properties updated successfully.' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">Loading Admin Portal...</div>;

  const currentEnv = config.appEnv;
  const isProd = currentEnv === 'production';
  const switchUrl = isProd ? config.devUrl : config.prodUrl;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-4 md:p-6 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col lg:flex-row lg:justify-between lg:items-center border-b border-slate-800 pb-6 gap-6">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 text-blue-400 mb-2">
              <Link href="/" className="hover:underline text-sm flex items-center"><Server size={14} className="mr-1"/> Dashboard</Link>
              <ChevronRight size={14} className="text-slate-600"/>
              <span className="text-sm text-slate-300">Admin Settings</span>
              <span className={`ml-2 px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest border ${
                isProd ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {currentEnv}
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight">System Properties</h1>
            <p className="text-slate-400 mt-1">Manage global engine configuration and integrations.</p>
          </div>
          
          <div className="flex items-center gap-4">
            <a 
              href={switchUrl}
              className="text-[10px] text-slate-500 hover:text-blue-400 transition-colors flex items-center gap-1 border border-slate-800 px-2 py-1 rounded-md hover:border-blue-500/30"
            >
              <Activity size={10} /> Switch to {isProd ? 'Dev' : 'Production'}
            </a>
          </div>
        </header>

        {message && (
          <div className={`p-4 rounded-xl border flex items-center gap-3 animate-in fade-in slide-in-from-top-2 ${
            message.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
          }`}>
            {message.type === 'success' ? <ShieldCheck size={20} /> : <AlertCircle size={20} />}
            <p className="text-sm font-medium">{message.text}</p>
          </div>
        )}

        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-slate-800 bg-slate-900/30">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Settings className="text-blue-400" size={20} /> Integration Settings
            </h3>
          </div>
          
          <div className="p-6 space-y-6">
            {settings.map((setting) => (
              <div key={setting.setting_key} className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                    {setting.setting_key.replace(/_/g, ' ')}
                  </label>
                  <span className="text-[10px] text-slate-600 font-mono">Last updated: {new Date(setting.updated_at).toLocaleString()}</span>
                </div>
                <input 
                  type="text" 
                  value={setting.setting_value}
                  onChange={(e) => updateSetting(setting.setting_key, e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-mono"
                  placeholder={`Enter value for ${setting.setting_key}...`}
                />
                <p className="text-[10px] text-slate-500 italic">
                  {setting.setting_key === 'discord_webhook_url' && "This URL is used by the engine to send real-time betting alerts to your Discord server."}
                </p>
              </div>
            ))}

            <div className="pt-4 flex justify-end">
              <button 
                onClick={saveSettings}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-bold text-sm transition-all flex items-center gap-2 shadow-lg shadow-blue-900/20"
              >
                {saving ? <Activity className="animate-spin" size={18} /> : <Save size={18} />}
                {saving ? 'Saving...' : 'Apply Changes'}
              </button>
            </div>
          </div>
        </div>

        <div className="p-6 bg-blue-600/5 border border-blue-500/10 rounded-2xl flex gap-4 items-start">
          <AlertCircle className="text-blue-400 shrink-0" size={20} />
          <div className="space-y-1">
            <p className="text-sm font-bold text-blue-300">Environment Override Active</p>
            <p className="text-xs text-slate-400 leading-relaxed">
              Properties saved here will persist in the <strong>{currentEnv}</strong> database. 
              The engine will prioritize these values over standard environment variables to prevent configuration drift.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
