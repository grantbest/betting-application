import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const res = await query('SELECT * FROM bet_tracking ORDER BY created_at DESC');
    return NextResponse.json(res.rows);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}

export async function PATCH(request: Request) {
  try {
    const { bet_id, result } = await request.json();
    if (!['WON', 'LOST', 'PENDING'].includes(result)) {
      return NextResponse.json({ error: 'Invalid result' }, { status: 400 });
    }
    await query('UPDATE bet_tracking SET result = $1 WHERE bet_id = $2', [result, bet_id]);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database error' }, { status: 500 });
  }
}
