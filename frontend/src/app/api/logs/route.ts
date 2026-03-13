import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const beads: any[] = [];
  const searchDirs = [
    "/app/.beads",
    "/Users/grantbest/Documents/Active/BettingApp/.beads",
    "/Users/grantbest/Documents/Active/Homelab/.beads"
  ];

  for (const dir of searchDirs) {
    try {
      if (fs.existsSync(dir)) {
        const files = fs.readdirSync(dir);
        for (const file of files) {
          if (file.endsWith(".json")) {
            const data = JSON.parse(fs.readFileSync(path.join(dir, file), "utf-8"));
            beads.push(data);
          }
        }
      }
    } catch (err) {
      console.error(`Error reading beads from ${dir}`, err);
    }
  }

  // Sort by date descending
  beads.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return NextResponse.json(beads);
}
