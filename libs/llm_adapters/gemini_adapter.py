import os
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from libs.llm_adapters.base import BaseLLMAdapter
from services.shared_kernel.domain.schemas import CallTurnBase


def _build_tools() -> types.Tool:
    return types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_knowledge",
            description="Retrieve grounded knowledge from the organization's knowledge base to answer a caller's question.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="The specific question to look up"
                    )
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="collect_caller_info",
            description="Collect specific information from the caller (e.g., name, phone number, email).",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "field_name": types.Schema(
                        type=types.Type.STRING,
                        description="The name of the field being collected"
                    ),
                    "field_value": types.Schema(
                        type=types.Type.STRING,
                        description="The value of the field provided by the caller"
                    )
                },
                required=["field_name", "field_value"]
            )
        ),
        types.FunctionDeclaration(
            name="trigger_escalation",
            description="Trigger an escalation to hand off the call to a human.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "reason": types.Schema(
                        type=types.Type.STRING,
                        description="The reason for the escalation"
                    )
                },
                required=["reason"]
            )
        ),
        types.FunctionDeclaration(
            name="end_call",
            description="End the call when the conversation is naturally finished.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "reason": types.Schema(
                        type=types.Type.STRING,
                        description="The reason for ending the call"
                    )
                }
            )
        )
    ])


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str = "gemini-3.5-flash-lite"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = model_name
        self.tools = _build_tools()

    def generate_response(self, system_prompt: str, turns: List[CallTurnBase], context: str = "") -> Dict[str, Any]:
        # Build the conversation contents (Gemini has no "system" role in contents;
        # system_prompt goes in a separate config field instead)
        contents = []

        if context:
            # Inject knowledge context as an early "model-visible" user note,
            # since Gemini has no equivalent of OpenAI's extra system message mid-list
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=f"[System note - Relevant Knowledge Context]\n{context}")]
                )
            )

        # for turn in turns:
        #     role = "user" if turn.speaker == "caller" else "model"
        #     contents.append(
        #         types.Content(role=role, parts=[types.Part(text=turn.text)])
        #     )
        for turn in turns:
            if turn.speaker == "caller":
                role = "user"
            elif turn.speaker == "ai":
                role = "model"
            else:
                # Orchestrator-injected notes (e.g. speaker="system" after a tool call).
                # Gemini has no mid-conversation system role, so fold these in as a
                # user-visible context note — this also keeps the turn sequence ending
                # on "user", which Gemini requires.
                role = "user"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=f"[System note: {turn.text}]" if turn.speaker not in ("caller", "ai") else turn.text)])
            )

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[self.tools],
            temperature=0.3
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )

        candidate = response.candidates[0]
        parts = candidate.content.parts

        # Check for a function call in the response parts
        for part in parts:
            if part.function_call:
                fc = part.function_call
                return {
                    "type": "tool_call",
                    "name": fc.name,
                    "arguments": dict(fc.args) if fc.args else {}
                }

        # No function call -> plain text message
        return {
            "type": "message",
            "text": response.text or ""
        }