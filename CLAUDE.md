# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is
MLB Betting Engine + Next.js Dashboard. The engine scans live games, evaluates dynamic rules from the DB, and generates AI-driven insights.

## Commands

### Backend (Engine)
```bash
pip install -r requirements.txt
python init_db.py             # Setup tables and seed data
python engine.py              # Start polling loop
```

### Frontend (Dashboard)
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
pytest tests/
```

## AI Insights (`ai_orchestrator.py`)
- Priority: **Gemini 1.5 Flash** (via direct API)
- Fallback: **OpenAI GPT-4o-mini**
- Emergency: **Ollama llama3** (Local)

## Rules Engine
- JSON-based conditions stored in `betting_rules` table.
- Managed via `/rules` page in the dashboard.
- Evaluated every 60s by `engine.py`.

## System Properties
- Global settings (like Discord Webhooks) stored in `system_settings` table.
- Managed via `/admin` page.

## Weather Service
- Fetches real-time game conditions from MLB Stats API.
- Fallback: 72°F / 5mph / Clear.
