import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function POST() {
  // Priority: Database Setting -> Environment Variable
  const settingsRes = await query("SELECT setting_value FROM system_settings WHERE setting_key = 'discord_webhook_url'");
  const webhookUrl = settingsRes.rows[0]?.setting_value || process.env.DISCORD_WEBHOOK_URL;

  if (!webhookUrl || webhookUrl.includes('dummy') || webhookUrl.includes('placeholder')) {
    return NextResponse.json({ error: 'No valid Discord webhook URL configured.' }, { status: 400 });
  }

  const embed = {
    title: "🧪 Test Alert",
    description: "This is a test alert from the WE do it inc. management dashboard.",
    color: 3447003,
    fields: [
      { name: "Status", value: "Functional", inline: true },
      { name: "Environment", value: "Production/Live", inline: true }
    ],
    footer: { text: "WE do it inc." }
  };

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ embeds: [embed] }),
    });

    if (!response.ok) throw new Error('Failed to send');

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to send test alert' }, { status: 500 });
  }
}
