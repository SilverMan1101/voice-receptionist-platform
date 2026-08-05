import redis
import json
from typing import List, Dict, Any

class CallStateStore:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.client = redis.from_url(redis_url, decode_responses=True)

    def get_turns(self, call_id: str) -> List[Dict[str, Any]]:
        data = self.client.get(f"call:{call_id}:turns")
        return json.loads(data) if data else []

    def add_turn(self, call_id: str, speaker: str, text: str):
        turns = self.get_turns(call_id)
        # We store index as part of the turn for reference
        turns.append({"turn_index": len(turns), "speaker": speaker, "text": text})
        self.client.set(f"call:{call_id}:turns", json.dumps(turns), ex=3600) # 1 hour TTL
        
    def get_collected_info(self, call_id: str) -> Dict[str, str]:
        data = self.client.get(f"call:{call_id}:info")
        return json.loads(data) if data else {}
        
    def add_collected_info(self, call_id: str, field_name: str, field_value: str):
        info = self.get_collected_info(call_id)
        info[field_name] = field_value
        self.client.set(f"call:{call_id}:info", json.dumps(info), ex=3600)
