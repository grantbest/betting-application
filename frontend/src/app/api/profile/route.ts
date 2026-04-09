import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ 
    user: 'admin', 
    settings: { theme: 'dark', notifications: true },
    version: 'Gastown v3.5'
  });
}
