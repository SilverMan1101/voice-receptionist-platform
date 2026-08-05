import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from libs.llm_adapters.base import BaseLLMAdapter
from services.shared_kernel.domain.schemas import CallTurnBase

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "retrieve_knowledge",
                    "description": "Retrieve grounded knowledge from the organization's knowledge base to answer a caller's question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The specific question to look up"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "collect_caller_info",
                    "description": "Collect specific information from the caller (e.g., name, phone number, email).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "field_name": {
                                "type": "string",
                                "description": "The name of the field being collected"
                            },
                            "field_value": {
                                "type": "string",
                                "description": "The value of the field provided by the caller"
                            }
                        },
                        "required": ["field_name", "field_value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_escalation",
                    "description": "Trigger an escalation to hand off the call to a human.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "The reason for the escalation"
                            }
                        },
                        "required": ["reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "end_call",
                    "description": "End the call when the conversation is naturally finished.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "The reason for ending the call"
                            }
                        }
                    }
                }
            }
        ]

    def generate_response(self, system_prompt: str, turns: List[CallTurnBase], context: str = "") -> Dict[str, Any]:
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({"role": "system", "content": f"Relevant Knowledge Context:\n{context}"})
            
        for turn in turns:
            role = "user" if turn.speaker == "caller" else "assistant"
            messages.append({"role": role, "content": turn.text})
            
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self.tools,
            temperature=0.3
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "type": "tool_call",
                "name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            }
        else:
            return {
                "type": "message",
                "text": message.content or ""
            }
