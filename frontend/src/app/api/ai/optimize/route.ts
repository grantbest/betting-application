import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const rulesRes = await query("SELECT rule_id, name, conditions_json FROM betting_rules WHERE status = 'ACTIVE'");
    const rules = rulesRes.rows.map(r => ({ id: r.rule_id, name: r.name, conditions: r.conditions_json }));

    const historyRes = await query("SELECT game_id, system_triggered, result FROM bet_tracking WHERE result != 'PENDING' ORDER BY created_at DESC LIMIT 50");
    const history = historyRes.rows.map(h => ({ game_id: h.game_id, system: h.system_triggered, result: h.result }));

    if (rules.length === 0 || history.length === 0) {
      return NextResponse.json({ 
        analysis: "Insufficient data for analysis. Please ensure you have active rules and completed bets." 
      });
    }

    const OLLAMA_BASE = process.env.OLLAMA_BASE_URL || 'http://host.docker.internal:11434';
    const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3';

    const systemPrompt = "You are an expert MLB Quantitative Analyst. Analyze stats and provide sharp, concise insights. Do not use conversational filler.";
    const prompt = `Review historical betting data and active rules.\n\nRules: ${JSON.stringify(rules)}\n\nHistory: ${JSON.stringify(history)}\n\nTask: Identify patterns in losses. Suggest specific tweaks to rule JSON conditions. Format with 'Findings' and 'Suggested Tweaks' sections.`;

    const response = await fetch(`${OLLAMA_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: prompt }
        ],
        stream: false
      })
    });

    const data = await response.json();
    return NextResponse.json({ analysis: data.message.content });

  } catch (error) {
    console.error('AI Optimization Error:', error);
    return NextResponse.json({ error: 'Failed to run AI strategy analysis.' }, { status: 500 });
  }
}
