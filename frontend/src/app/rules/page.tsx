'use client';

import { useState, useEffect } from 'react';
import { Plus, Trash2, Save, Play, Pause, Server, ChevronRight, Activity } from 'lucide-react';
import Link from 'next/link';

interface RuleCondition {
  attribute: string;
  operator: string;
  value: string | number;
}

interface RuleGroup {
  logic: 'AND' | 'OR';
  conditions: (RuleCondition | RuleGroup)[];
}

interface BettingRule {
  rule_id?: number;
  name: string;
  description: string;
  status: 'ACTIVE' | 'DRY_RUN' | 'INACTIVE';
  conditions_json: RuleGroup;
  action_type: string;
  action_config: any;
}

const ATTRIBUTES = [
  { id: 'inning', label: 'Current Inning', type: 'number' },
  { id: 'runs_scored_half', label: 'Runs Scored (This Half)', type: 'number' },
  { id: 'baserunners', label: 'Baserunners', type: 'number' },
  { id: 'pitching_team_bullpen_rank', label: 'Pitching Team Bullpen Rank', type: 'number' },
  { id: 'score_diff', label: 'Score Differential (Home - Away)', type: 'number' }
];

const OPERATORS = [
  { id: '==', label: 'Equals' },
  { id: '!=', label: 'Not Equals' },
  { id: '>', label: 'Greater Than' },
  { id: '>=', label: 'Greater or Equal' },
  { id: '<', label: 'Less Than' },
  { id: '<=', label: 'Less or Equal' }
];

const DEFAULT_GROUP: RuleGroup = { logic: 'AND', conditions: [{ attribute: 'inning', operator: '>=', value: 7 }] };

interface AppConfig {
  appEnv: string;
  devUrl: string;
  prodUrl: string;
  discordChannelUrl: string;
}

export default function RulesEngine() {
  const [rules, setRules] = useState<BettingRule[]>([]);
  const [editingRule, setEditingRule] = useState<BettingRule | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);

  const fetchInitialData = async () => {
    try {
      const [rulesRes, configRes] = await Promise.all([
        fetch('/api/rules'),
        fetch('/api/config')
      ]);
      const rawRules = await rulesRes.json();
      
      const sanitizedRules = rawRules.map((rule: BettingRule) => ({
        ...rule,
        conditions_json: rule.conditions_json && typeof rule.conditions_json === 'object' 
          ? {
              logic: rule.conditions_json.logic || 'AND',
              conditions: Array.isArray(rule.conditions_json.conditions) ? rule.conditions_json.conditions : []
            }
          : { logic: 'AND', conditions: [] }
      }));

      setRules(sanitizedRules);
      setConfig(await configRes.json());
    } catch (err) {
      console.error('Failed to fetch data', err);
    }
  };

  const fetchRules = async () => {
    try {
      const res = await fetch('/api/rules');
      const data = await res.json();
      
      // Ensure every rule has a valid conditions_json structure to prevent React crashes
      const sanitizedRules = data.map((rule: BettingRule) => ({
        ...rule,
        conditions_json: rule.conditions_json && typeof rule.conditions_json === 'object' 
          ? {
              logic: rule.conditions_json.logic || 'AND',
              conditions: Array.isArray(rule.conditions_json.conditions) ? rule.conditions_json.conditions : []
            }
          : { logic: 'AND', conditions: [] }
      }));
      
      setRules(sanitizedRules);
    } catch (err) {
      console.error('Failed to fetch rules', err);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  if (!config) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">Loading Configuration...</div>;

  const saveRule = async () => {
    if (!editingRule) return;
    
    const method = editingRule.rule_id ? 'PUT' : 'POST';
    await fetch('/api/rules', {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editingRule)
    });
    
    setEditingRule(null);
    fetchRules();
  };

  const deleteRule = async (id: number) => {
    if(!confirm('Are you sure?')) return;
    await fetch(`/api/rules?id=${id}`, { method: 'DELETE' });
    fetchRules();
  };

  const currentEnv = config?.appEnv || 'development';
  const isProd = currentEnv === 'production';
  const switchUrl = isProd ? config?.devUrl : config?.prodUrl;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex justify-between items-center border-b border-slate-800 pb-6">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 text-blue-400 mb-2">
              <Link href="/" className="hover:underline text-sm flex items-center"><Server size={14} className="mr-1"/> Dashboard</Link>
              <ChevronRight size={14} className="text-slate-600"/>
              <span className="text-sm text-slate-300">Rules Engine</span>
              <span className={`ml-2 px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest border ${
                isProd ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {currentEnv}
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Betting Rules Engine</h1>
            <div className="flex items-center gap-4 mt-1">
              <p className="text-slate-400">Design and test logical triggers for the MLB engine.</p>
              <a 
                href={switchUrl}
                className="text-[10px] text-slate-500 hover:text-blue-400 transition-colors flex items-center gap-1 border border-slate-800 px-2 py-1 rounded-md hover:border-blue-500/30"
              >
                <Activity size={10} /> Switch to {isProd ? 'Dev' : 'Production'}
              </a>
            </div>
          </div>
          <button 
            onClick={() => setEditingRule({ name: 'New Rule', description: '', status: 'DRY_RUN', conditions_json: DEFAULT_GROUP, action_type: 'DISCORD_ALERT', action_config: { odds: -110, p: 0.55 } })}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
          >
            <Plus size={16} /> Create Rule
          </button>
        </header>

        {editingRule ? (
          <RuleEditor rule={editingRule} setRule={setEditingRule} onSave={saveRule} onCancel={() => setEditingRule(null)} />
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {rules.length === 0 ? (
               <div className="text-center py-12 bg-slate-900/50 rounded-xl border border-slate-800 text-slate-500">
                 No rules defined yet. Create your first rule above.
               </div>
            ) : rules.map(rule => (
              <div key={rule.rule_id} className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 flex justify-between items-center group">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-lg font-bold">{rule.name}</h3>
                    <StatusBadge status={rule.status} />
                  </div>
                  <p className="text-sm text-slate-400">{rule.description || "No description provided."}</p>
                </div>
                <div className="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => setEditingRule(rule)} className="text-blue-400 hover:text-blue-300 px-3 py-1 bg-blue-500/10 rounded-md text-sm">Edit</button>
                  <button onClick={() => deleteRule(rule.rule_id!)} className="text-rose-400 hover:text-rose-300 p-2 bg-rose-500/10 rounded-md"><Trash2 size={16}/></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, { bg: string, icon: React.ReactNode }> = {
    ACTIVE: { bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', icon: <Play size={12} className="mr-1"/> },
    DRY_RUN: { bg: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20', icon: <Activity size={12} className="mr-1"/> },
    INACTIVE: { bg: 'bg-slate-500/10 text-slate-400 border-slate-500/20', icon: <Pause size={12} className="mr-1"/> },
  };
  const s = styles[status] || styles.INACTIVE;
  return (
    <span className={`px-2 py-1 rounded text-[10px] font-bold border flex items-center w-fit ${s.bg}`}>
      {s.icon} {status}
    </span>
  );
}

function RuleEditor({ rule, setRule, onSave, onCancel }: { rule: BettingRule, setRule: (r: BettingRule) => void, onSave: () => void, onCancel: () => void }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4">
      
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-400">Rule Name</label>
          <input 
            type="text" 
            value={rule.name} 
            onChange={(e) => setRule({...rule, name: e.target.value})}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-400">Status</label>
          <select 
            value={rule.status} 
            onChange={(e) => setRule({...rule, status: e.target.value as any})}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
          >
            <option value="DRY_RUN">Dry Run (Log Only)</option>
            <option value="ACTIVE">Active (Send Alerts)</option>
            <option value="INACTIVE">Inactive (Disabled)</option>
          </select>
        </div>
        <div className="col-span-2 space-y-2">
          <label className="text-sm font-medium text-slate-400">Description</label>
          <input 
            type="text" 
            value={rule.description} 
            onChange={(e) => setRule({...rule, description: e.target.value})}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
            placeholder="What does this rule look for?"
          />
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold border-b border-slate-800 pb-2">Conditions (The "Sentence Builder")</h3>
        <p className="text-xs text-slate-500">Define the logical triggers. If all outer conditions evaluate to true, the action fires.</p>
        
        {/* Simple Group Editor for V1. Assuming 1 root group for now. */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-400">Match</span>
            <select 
              value={rule.conditions_json.logic}
              onChange={(e) => setRule({...rule, conditions_json: {...rule.conditions_json, logic: e.target.value as 'AND' | 'OR'}})}
              className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm font-bold text-blue-400 focus:outline-none"
            >
              <option value="AND">ALL</option>
              <option value="OR">ANY</option>
            </select>
            <span className="text-sm font-medium text-slate-400">of the following rules:</span>
          </div>

          <div className="space-y-2 pl-4 border-l-2 border-slate-800">
            {rule.conditions_json.conditions.map((cond: any, idx) => (
              <div key={idx} className="flex gap-2 items-center">
                <select 
                  value={cond.attribute}
                  onChange={(e) => {
                    const newConds = [...rule.conditions_json.conditions];
                    (newConds[idx] as RuleCondition).attribute = e.target.value;
                    setRule({...rule, conditions_json: {...rule.conditions_json, conditions: newConds}});
                  }}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none min-w-[200px]"
                >
                  {ATTRIBUTES.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
                </select>

                <select 
                  value={cond.operator}
                  onChange={(e) => {
                    const newConds = [...rule.conditions_json.conditions];
                    (newConds[idx] as RuleCondition).operator = e.target.value;
                    setRule({...rule, conditions_json: {...rule.conditions_json, conditions: newConds}});
                  }}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none font-bold text-emerald-400"
                >
                  {OPERATORS.map(o => <option key={o.id} value={o.id}>{o.label}</option>)}
                </select>

                <input 
                  type="number"
                  value={cond.value}
                  onChange={(e) => {
                    const newConds = [...rule.conditions_json.conditions];
                    (newConds[idx] as RuleCondition).value = Number(e.target.value);
                    setRule({...rule, conditions_json: {...rule.conditions_json, conditions: newConds}});
                  }}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none w-24"
                />

                <button 
                  onClick={() => {
                    const newConds = rule.conditions_json.conditions.filter((_, i) => i !== idx);
                    setRule({...rule, conditions_json: {...rule.conditions_json, conditions: newConds}});
                  }}
                  className="p-2 text-rose-500 hover:bg-rose-500/10 rounded-lg ml-2"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
            
            <button 
              onClick={() => {
                const newConds = [...rule.conditions_json.conditions, { attribute: 'inning', operator: '==', value: 1 }];
                setRule({...rule, conditions_json: {...rule.conditions_json, conditions: newConds}});
              }}
              className="text-sm font-medium text-blue-400 hover:text-blue-300 flex items-center gap-1 mt-4"
            >
              <Plus size={14} /> Add Condition
            </button>
          </div>
        </div>

      </div>

      <div className="flex justify-end gap-3 pt-6 border-t border-slate-800">
        <button onClick={onCancel} className="px-4 py-2 text-slate-400 hover:text-slate-200">Cancel</button>
        <button onClick={onSave} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2">
          <Save size={16} /> Save Rule
        </button>
      </div>
    </div>
  );
}
