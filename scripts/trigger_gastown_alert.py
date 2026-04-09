import asyncio
import os
import sys
import json
import httpx
from typing import Dict, Any
from temporalio.client import Client

async def trigger_alert(system_name, game_id, bet_target, odds, stake, ai_insight, deep_link_url, game_info, inning=None):
    """
    Triggers a Gastown-native alert via Temporal.
    """
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL missing.")
        return

    # 1. Prepare Payload (matching the standard embed format)
    title = f"📈 {system_name} Opportunity"
    if game_info:
        title = f"📈 {game_info} | {system_name}"

    description = f"A high-probability betting opportunity has been identified.\n\n"
    if ai_insight:
        description += f"🤖 **AI Analyst Insight:**\n*{ai_insight}*\n\n"
    
    if deep_link_url:
        description += f"🚀 **[ONE-TAP BET: OPEN SLIP]({deep_link_url})**"

    fields = [
        {"name": "Game ID", "value": str(game_id), "inline": True},
        {"name": "Bet", "value": bet_target, "inline": True},
        {"name": "Odds", "value": str(odds), "inline": True},
    ]

    if inning:
        fields.append({"name": "Inning", "value": inning, "inline": True})

    fields.extend([
        {"name": "Stake", "value": f"{stake:.2%}", "inline": True},
        {"name": "Detected At", "value": now, "inline": True}
    ])

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": 3447003,
            "fields": fields,
            "footer": {"text": "GASTOWN NATIVE ALERTING | Please Bet Responsibly"}
        }]
    }

    alert_data = {
        "webhook_url": webhook_url,
        "payload": payload,
        "game_id": str(game_id)
    }

    try:
        # SRE: Use the Sidecar Gateway exclusively
        sidecar_url = "http://localhost:8001"
        
        print(f"🚀 Dispatching Gastown Alert for game {game_id} via Sidecar...")
        
        # 1. Create the Bead in Vikunja
        payload = {
            "title": f"[ALERT] {game_info or game_id}",
            "description": f"Actionable Alert for {system_name}",
            "project_id": 1,
            "labels": [{"title": "Component: Betting"}] # ATTR-BASED ROUTING
        }
        
        with httpx.Client() as client:
            resp = client.put(f"{sidecar_url}/projects/1/tasks", json=payload)
            resp.raise_for_status()
            task = resp.json()
            bead_id = str(task['id'])
            
            # 2. Add metadata
            metadata = {
                "stage": "DOING",
                "context": {"alert_data": alert_data, "type": "DISCORD_ALERT"}
            }
            client.post(f"{sidecar_url}/tasks/{bead_id}", json={"description": f"{payload['description']}\n\n--- AGENT METADATA ---\n{json.dumps(metadata)}"})
            
            # 3. Trigger Workflow in the correct namespace
            sys.path.append("/Users/grantbest/Documents/Active/BestFam-Orchestrator")
            from src.utils.namespace_manager import NamespaceManager
            target_ns = "betting-app" # Forced for alerts
            target_queue = NamespaceManager.get_queue_for_namespace(target_ns)
            
            from temporalio.client import Client
            from src.workers.mayor_workflow import MayorWorkflow
            
            temporal_client = await Client.connect(temporal_address, namespace=target_ns)
            await temporal_client.start_workflow(
                MayorWorkflow.run,
                args=[bead_id, "Doing"],
                id=f"alert-workflow-{bead_id}",
                task_queue=target_queue,
            )
            
        print(f"✅ Alert Bead {bead_id} dispatched to {target_ns} namespace.")
        
    except Exception as e:
        print(f"❌ Failed to dispatch Gastown alert: {e}")

if __name__ == "__main__":
    # args: sys_name, g_id, target, odds, stake, insight, link, info, [inning]
    inning = sys.argv[9] if len(sys.argv) > 9 else None
    asyncio.run(trigger_alert(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6], sys.argv[7], sys.argv[8], inning))
