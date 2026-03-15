import { NextResponse } from "next/server";
import postgres from "postgres";

const sql = postgres(process.env.DATABASE_URL || "postgresql://postgres:postgres@postgres:5432/homelab");

export async function GET() {
  try {
    const messages = await sql`SELECT * FROM agent_chat ORDER BY created_at ASC LIMIT 100`;
    return NextResponse.json(messages);
  } catch (err) {
    return NextResponse.json({ error: "Failed to fetch chat" }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { role, content } = await req.json();
    const newMessage = await sql`
      INSERT INTO agent_chat (role, content) 
      VALUES (${role}, ${content}) 
      RETURNING *
    `;
    return NextResponse.json(newMessage[0]);
  } catch (err) {
    return NextResponse.json({ error: "Failed to send message" }, { status: 500 });
  }
}
