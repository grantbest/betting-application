import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const res = await query('SELECT * FROM system_settings');
    return NextResponse.json(res.rows);
  } catch (error) {
    console.error('Settings GET Error:', error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { setting_key, setting_value } = await request.json();
    if (!setting_key || setting_value === undefined) {
      return NextResponse.json({ error: 'Key and Value are required' }, { status: 400 });
    }

    const res = await query(
      `INSERT INTO system_settings (setting_key, setting_value, updated_at) 
       VALUES ($1, $2, CURRENT_TIMESTAMP) 
       ON CONFLICT (setting_key) 
       DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = CURRENT_TIMESTAMP 
       RETURNING *`,
      [setting_key, setting_value]
    );
    return NextResponse.json(res.rows[0]);
  } catch (error) {
    console.error('Settings POST Error:', error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}
