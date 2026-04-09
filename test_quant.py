import json
from services.quant_service import QuantService
import os

qs = QuantService()
state = {"inning": 3, "score_diff": 0}
print(f"Testing with state: {state}")
res = qs.get_similarity_context(state)
print(f"Result: {json.dumps(res, indent=2)}")

state = {"inning": 9, "score_diff": 5}
print(f"\nTesting with state: {state}")
res2 = qs.get_similarity_context(state)
print(f"Result: {json.dumps(res2, indent=2)}")
