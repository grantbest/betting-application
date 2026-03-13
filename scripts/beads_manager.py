import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# Identify the root of the project by looking for the .beads folder
def get_beads_dir():
    current_path = Path(__file__).resolve().parent
    while current_path != current_path.parent:
        beads_path = current_path / '.beads'
        if beads_path.exists() and beads_path.is_dir():
            return beads_path
        current_path = current_path.parent
    raise FileNotFoundError("Could not find '.beads' directory. Please ensure it exists at the project root.")

BEADS_DIR = get_beads_dir()

def create_bead(title, description, requesting_agent, assigned_agent=None):
    """Creates a new bead (task) as a JSON file."""
    bead_id = str(uuid.uuid4())
    bead_data = {
        "id": bead_id,
        "title": title,
        "description": description,
        "status": "pending",
        "requesting_agent": requesting_agent,
        "assigned_agent": assigned_agent,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "context": {},
        "resolution": None
    }
    
    file_path = BEADS_DIR / f"{bead_id}.json"
    with open(file_path, "w") as f:
        json.dump(bead_data, f, indent=4)
    print(f"Created bead: {bead_id}")
    return bead_id

def read_bead(bead_id):
    """Reads a specific bead."""
    file_path = BEADS_DIR / f"{bead_id}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Bead {bead_id} not found.")
    
    with open(file_path, "r") as f:
        return json.load(f)

def update_bead(bead_id, updates):
    """Updates an existing bead."""
    bead_data = read_bead(bead_id)
    bead_data.update(updates)
    bead_data["updated_at"] = datetime.utcnow().isoformat()
    
    file_path = BEADS_DIR / f"{bead_id}.json"
    with open(file_path, "w") as f:
        json.dump(bead_data, f, indent=4)
    print(f"Updated bead: {bead_id}")
    return bead_data

def list_beads(status=None):
    """Lists all beads, optionally filtered by status."""
    beads = []
    for file_path in BEADS_DIR.glob("*.json"):
        with open(file_path, "r") as f:
            data = json.load(f)
            if status is None or data.get("status") == status:
                beads.append(data)
    return beads

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        for b in list_beads():
            print(f"[{b['status'].upper()}] {b['id']}: {b['title']}")
