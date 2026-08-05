import abc
from typing import List, Dict, Any, Optional
from services.shared_kernel.domain.schemas import CallTurnBase

class BaseLLMAdapter(abc.ABC):
    @abc.abstractmethod
    def generate_response(self, system_prompt: str, turns: List[CallTurnBase], context: str = "") -> Dict[str, Any]:
        """
        Generate a response or propose a tool call.
        Returns a dict that can be:
        {"type": "message", "text": "..."}
        or
        {"type": "tool_call", "name": "...", "arguments": {...}}
        """
        pass
