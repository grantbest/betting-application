import { NextResponse } from 'next/server';

export async function GET() {
  const weatherData = [
    { city: 'New York', temp: '72°F', condition: 'Clear', wind: '5mph' },
    { city: 'Chicago', temp: '48°F', condition: 'Cloudy', wind: '12mph' },
    { city: 'Los Angeles', temp: '85°F', condition: 'Sunny', wind: '3mph' },
    { city: 'Seattle', temp: '55°F', condition: 'Rain', wind: '8mph' }
  ];
  
  return NextResponse.json({ 
    status: 'success', 
    data: weatherData,
    timestamp: new Date().toISOString(),
    tracer: 'Gastown v4.2 Resiliency Proof'
  });
}
