import { NextResponse } from "next/server";
import { Connection, Client } from "@temporalio/client";
import { createClient } from "redis";
import postgres from "postgres";
import fs from "fs";

export async function GET() {
  const healthData: any = {
    timestamp: new Date().toISOString(),
    infra: {},
    services: {},
    agents: {
      pending_beads: 0,
      completed_beads: 0
    }
  };

  // 1. Database (Postgres)
  try {
    const sql = postgres(process.env.DATABASE_URL || "postgresql://postgres:postgres@postgres:5432/homelab");
    await sql`SELECT 1`;
    healthData.infra.postgres = "HEALTHY";
  } catch (err) {
    healthData.infra.postgres = "UNHEALTHY";
  }

  // 2. Cache (Redis)
  try {
    const redis = createClient({ url: process.env.REDIS_URL || "redis://redis:6379" });
    await redis.connect();
    await redis.ping();
    await redis.disconnect();
    healthData.infra.redis = "HEALTHY";
  } catch (err) {
    healthData.infra.redis = "UNHEALTHY";
  }

  // 3. Orchestration (Temporal)
  try {
    const connection = await Connection.connect({ address: "temporal:7233" });
    const client = new Client({ connection });
    await client.workflowService.getSystemInfo({});
    healthData.infra.temporal = "HEALTHY";
  } catch (err) {
    healthData.infra.temporal = "UNHEALTHY";
  }

  // 4. App Context (Beads)
  try {
    const beadsDir = "/app/.beads";
    if (fs.existsSync(beadsDir)) {
      const files = fs.readdirSync(beadsDir);
      healthData.agents.pending_beads = files.length;
    }
  } catch (err) {
    healthData.agents.error = "COULD_NOT_READ_BEADS";
  }

  return NextResponse.json(healthData);
}
