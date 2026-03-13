import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const res = await query('SELECT * FROM betting_rules ORDER BY created_at DESC');
    return NextResponse.json(res.rows);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, description, status, conditions_json, action_type, action_config } = body;
    
    const res = await query(
      `INSERT INTO betting_rules (name, description, status, conditions_json, action_type, action_config) 
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [name, description, status || 'DRY_RUN', conditions_json, action_type || 'DISCORD_ALERT', action_config || {}]
    );
    return NextResponse.json(res.rows[0]);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json();
    const { rule_id, name, description, status, conditions_json, action_type, action_config } = body;
    
    const res = await query(
      `UPDATE betting_rules 
       SET name = $1, description = $2, status = $3, conditions_json = $4, action_type = $5, action_config = $6 
       WHERE rule_id = $7 RETURNING *`,
      [name, description, status, conditions_json, action_type, action_config, rule_id]
    );
    return NextResponse.json(res.rows[0]);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const url = new URL(request.url);
    const id = url.searchParams.get('id');
    if (!id) return NextResponse.json({ error: 'ID required' }, { status: 400 });
    
    await query('DELETE FROM betting_rules WHERE rule_id = $1', [id]);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}
