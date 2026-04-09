import { NextResponse } from 'next/server';

export async function GET() {
  const matches = [
    { id: 1, teamA: 'NYY', teamB: 'LAD', score: '3-2', winProb: 0.65 },
    { id: 2, teamA: 'BOS', teamB: 'HOU', score: '1-5', winProb: 0.15 }
  ];
  return NextResponse.json({ status: 'live', matches, timestamp: new Date().toISOString() });
}
