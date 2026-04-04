import asyncio
import nats
from nats.js.errors import TimeoutError
import json
import os

class NATSContinuity:
    """
    Local subscriber that ensures the MacBook 'catches up' 
    on MLB events missed while offline.
    """
    def __init__(self):
        self.nats_url = os.getenv("NATS_URL", "nats://control.bestfam.us:4222")
        self.stream_name = "MLB_EVENTS"
        self.subject = "mlb.>"

    async def run(self):
        print(f"📡 Connecting to Control Plane NATS at {self.nats_url}...")
        try:
            nc = await nats.connect(self.nats_url)
            js = nc.jetstream()

            # Create a durable consumer so NATS remembers where we left off
            # 'macbook-compute-plane' is the unique ID for this laptop
            sub = await js.pull_subscribe(self.subject, "macbook-compute-plane")

            print("✅ Connection Established. Replaying missed events...")

            while True:
                try:
                    msgs = await sub.fetch(10, timeout=1)
                    for msg in msgs:
                        data = json.loads(msg.data.decode())
                        print(f"📥 Received Catch-up Event: {data.get('event_type')}")
                        
                        # LOGIC: Pass to QuantEngine for backfill analysis
                        # self.process_event(data)
                        
                        await msg.ack()
                except TimeoutError:
                    # No new messages in the stream
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"⚠️ Error in fetch loop: {e}")
                    await asyncio.sleep(5)

        except Exception as e:
            print(f"❌ Failed to connect to NATS: {e}")

if __name__ == "__main__":
    continuity = NATSContinuity()
    asyncio.run(continuity.run())
