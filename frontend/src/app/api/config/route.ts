import { NextResponse } from 'next/server';

export async function GET() {
  // Use non-prefixed variables to ensure they are read at RUNTIME on the server
  return NextResponse.json({
    appEnv: process.env.APP_ENV || 'development',
    devUrl: process.env.DEV_URL || 'http://localhost:3000',
    prodUrl: process.env.PROD_URL || 'http://localhost:3001',
    discordChannelUrl: process.env.DISCORD_CHANNEL_URL || 'https://discord.com/channels/your-channel-id',
  });
}
