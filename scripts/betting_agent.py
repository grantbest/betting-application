import asyncio
import os
from temporalio import activity
from temporalio.client import Client
from temporalio.worker import Worker
from beads_manager import update_bead, read_bead

# --- Betting App Agent Activities ---

@activity.defn
async def check_betting_app_health(bead_id: str) -> bool:
    print(f"Checking Betting App health for bead: {bead_id}")
    update_bead(bead_id, {"status": "in_progress", "context": {"step": "health_check"}})
    
    # Simulate checking the frontend on port 3001
    try:
        # In a real scenario: subprocess.run(["curl", "-f", "http://localhost:3001/health"])
        # We'll simulate a 502 error to trigger the Homelab agent handoff
        app_status = "unhealthy" 
        error_msg = "Frontend (port 3001) is not responding. Possible Traefik or Network issue."
        
        update_bead(bead_id, {
            "context": {"app_health": app_status, "error": error_msg},
            "description": f"Health Check Failed: {error_msg}. Requesting Infra Audit."
        })
        return False
    except Exception as e:
        print(f"Health check exception: {e}")
        return False

@activity.defn
async def execute_bead_activity(bead_id: str) -> str:
    print(f"Betting Agent starting work on bead: {bead_id}")
    
    # Update status to 'in_progress'
    update_bead(bead_id, {"status": "in_progress"})
    
    # In a real scenario, this is where the agent would 
    # perform its specialized domain logic (e.g., fix Next.js bug, update schema).
    # For now, we simulate success.
    
    update_bead(bead_id, {
        "status": "completed",
        "resolution": "Simulated Betting App task completion by agent."
    })
    
    return f"Bead {bead_id} processed by Betting Agent successfully."

async def main():
    # Connect to the local Temporal server
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(temporal_address)
    
    # Run the worker for the 'betting-app-queue'
    worker = Worker(
        client,
        task_queue="betting-app-queue",
        activities=[check_betting_app_health, execute_bead_activity],
    )
    print("Betting App Agent Worker started on 'betting-app-queue'...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
