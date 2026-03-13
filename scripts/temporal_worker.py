import asyncio
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from beads_manager import update_bead, read_bead

# Define the activity that the agent will perform
@activity.defn
async def execute_bead_activity(bead_id: str) -> str:
    print(f"Agent starting work on bead: {bead_id}")
    
    # Update status to 'in_progress'
    update_bead(bead_id, {"status": "in_progress"})
    
    # In a real scenario, this is where the agent would 
    # perform its specialized domain logic (Homelab or BettingApp).
    # For now, we simulate success.
    
    update_bead(bead_id, {
        "status": "completed",
        "resolution": "Simulated task completion by agent."
    })
    
    return f"Bead {bead_id} processed successfully."

async def main():
    # Connect to the local Temporal server
    client = await Client.connect("localhost:7233")
    
    # Run the worker for the 'betting-app-queue'
    worker = Worker(
        client,
        task_queue="betting-app-queue",
        activities=[execute_bead_activity],
    )
    print("Betting App Agent Worker started...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
