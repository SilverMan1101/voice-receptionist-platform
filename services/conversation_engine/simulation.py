import sys
import os
import uuid
from dotenv import load_dotenv
# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from libs.llm_adapters.openai_adapter import OpenAIAdapter
from libs.llm_adapters.gemini_adapter import GeminiAdapter
from services.conversation_engine.infrastructure.redis_store import CallStateStore
from services.conversation_engine.infrastructure.knowledge_client import KnowledgeClient
from services.conversation_engine.application.orchestrator import ConversationOrchestrator
from services.shared_kernel.domain.schemas import BusinessRuleResponse
load_dotenv()
def main():
    print("Initializing Conversation Engine Simulation...")
    
    # Check API Key
    # if not os.environ.get("OPENAI_API_KEY"):
    #     print("ERROR: OPENAI_API_KEY environment variable is not set.")
    #     sys.exit(1)

    if not os.environ.get("GEMINI_API_KEY"):
       print("ERROR: GEMINI_API_KEY environment variable is not set.")
       sys.exit(1)
    
    # llm = OpenAIAdapter(model_name="gpt-4o-mini")
    llm = GeminiAdapter(model_name="gemini-3.5-flash-lite")
    state = CallStateStore(redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    knowledge_client = KnowledgeClient(base_url=os.environ.get("KNOWLEDGE_SERVICE_URL", "http://127.0.0.1:8000"))
    
    org_id = uuid.uuid4()
    
    # Mock business rules
    rules = [
        BusinessRuleResponse(
            id=uuid.uuid4(),
            organization_id=org_id,
            rule_type="escalation",
            condition={"trigger_type": "explicit_request"},
            action={"fallback_message": "Connecting you to our team now."},
            active=True
        ),
        BusinessRuleResponse(
            id=uuid.uuid4(),
            organization_id=org_id,
            rule_type="escalation",
            condition={"trigger_type": "low_confidence"},
            action={"fallback_message": "I want to make sure you get the right answer. Transferring you to a specialist."},
            active=True
        )
    ]
    
    orchestrator = ConversationOrchestrator(llm, state, knowledge_client, rules)
    
    call_id = str(uuid.uuid4())
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjAyMjkwOC05MzI4LTRhNGYtYTAwZC03OWJkM2ZhZTQ5NzQiLCJvcmdfaWQiOiJjNTU3MGFjZS1iMjk0LTQ0ZTktYjRlNi1hZmYyZWRhMTMwNGUiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3ODY5MDk2MjZ9.3Gbat6Q1Gmp7nNwu4RkwNLnE0_dnCRkfe-jV0fiwQYk"
    
    print("\n--- Simulation Started ---")
    print("Type 'quit' or 'exit' to end the simulation.\n")
    
    while True:
        try:
            user_input = input("Caller: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            if not user_input.strip():
                print("AI: I didn't catch that — could you say that again?")
                continue
            response = orchestrator.process_turn(call_id, str(org_id), token, user_input)
            
            if response["action"] == "reply":
                print(f"AI: {response['text']}")
            elif response["action"] == "escalate":
                print(f"AI (ESCALATING): {response['text']} [Reason: {response['reason']}]")
                break
            elif response["action"] == "end_call":
                print(f"AI (ENDING CALL): [Reason: {response['reason']}]")
                break
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Simulation Error: {str(e)}")
            break

if __name__ == "__main__":
    main()
