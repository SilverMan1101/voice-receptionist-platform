import os
import requests
from typing import Dict, Any, List

class KnowledgeClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("KNOWLEDGE_SERVICE_URL", "http://127.0.0.1:8000")

    def query(self, token: str, query_text: str, limit: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Calls the knowledge_service retrieval endpoint.
        Returns the raw results, including the `is_confident` flag.
        """
        url = f"{self.base_url}/api/v1/knowledge/query"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "query": query_text,
            "limit": limit,
            "threshold": threshold
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5.0)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            # Re-raise to let Orchestrator handle fallback
            raise RuntimeError(f"Failed to retrieve knowledge: {str(e)}")
