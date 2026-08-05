import pytest
from unittest.mock import MagicMock
from services.conversation_engine.application.orchestrator import ConversationOrchestrator
from services.shared_kernel.domain.schemas import BusinessRuleResponse

class MockStateStore:
    def add_turn(self, call_id, speaker, text): pass
    def get_turns(self, call_id): return []
    def add_collected_info(self, call_id, field, val): pass

class MockLLMAdapter:
    def __init__(self, response_dict):
        self.response_dict = response_dict
        
    def generate_response(self, system_prompt, turns, context=""):
        return self.response_dict

class MockKnowledgeClient:
    def query(self, token, query_text):
        return []

def test_llm_cannot_bypass_tool_validation():
    # LLM hallucinates an invalid tool call not defined in the contract
    bad_response = {
        "type": "tool_call",
        "name": "direct_db_update", 
        "arguments": {"user_id": "123", "status": "approved"}
    }
    
    llm = MockLLMAdapter(bad_response)
    state = MockStateStore()
    knowledge = MockKnowledgeClient()
    
    orchestrator = ConversationOrchestrator(llm, state, knowledge, rules=[])
    
    response = orchestrator.process_turn("call_123", "org_123", "token", "Hello")
    
    # Engine must validate the tool. Since "direct_db_update" is not recognized, 
    # it treats it as a failure/timeout and degrades gracefully instead of crashing.
    assert response["action"] == "escalate"
    assert response["reason"] == "System failure or timeout"

def test_orchestrator_degrades_on_knowledge_timeout():
    # LLM correctly asks for knowledge
    knowledge_request = {
        "type": "tool_call",
        "name": "retrieve_knowledge", 
        "arguments": {"query": "What are your hours?"}
    }
    
    llm = MockLLMAdapter(knowledge_request)
    state = MockStateStore()
    
    class ThrowingKnowledgeClient:
        def query(self, token, query_text):
            raise Exception("Timeout connecting to knowledge service")
            
    knowledge = ThrowingKnowledgeClient()
    
    orchestrator = ConversationOrchestrator(llm, state, knowledge, rules=[])
    response = orchestrator.process_turn("call_123", "org_123", "token", "Hours?")
    
    # Must escalate safely due to downstream failure
    assert response["action"] == "escalate"
    assert response["reason"] == "System failure or timeout"
