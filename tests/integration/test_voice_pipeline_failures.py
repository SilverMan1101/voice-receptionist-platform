import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from services.conversation_engine.application.orchestrator import ConversationOrchestrator
from services.conversation_engine.domain.business_rules_engine import BusinessRulesEngine
from services.shared_kernel.domain.schemas import BusinessRuleResponse
import uuid

@pytest.fixture
def mock_dependencies():
    llm = AsyncMock()
    state = MagicMock()
    # Ensure state tracking doesn't break
    state.get_turns.return_value = []
    state.get_collected_info.return_value = {}
    
    knowledge_client = MagicMock()
    rules = [
        BusinessRuleResponse(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            rule_type="escalation",
            condition={"trigger_type": "timeout"},
            action={"fallback_message": "System unavailable, transferring."},
            active=True
        )
    ]
    
    orchestrator = ConversationOrchestrator(llm, state, knowledge_client, rules)
    return orchestrator, llm, state, knowledge_client

def test_pipeline_failure_degrades_gracefully(mock_dependencies):
    """
    Tests that if the LLM downstream fails (e.g. timeout), the ConversationEngine
    does not crash but instead falls back to the scripted timeout escalation rule.
    """
    orchestrator, llm, state, knowledge_client = mock_dependencies
    
    # Simulate an LLM timeout/failure
    llm.generate_response.side_effect = Exception("Connection Timeout")
    
    # Process turn
    response = orchestrator.process_turn(
        call_id="call-123",
        organization_id="org-123",
        token="token",
        user_text="Hello?"
    )
    
    # Assert it gracefully escalates rather than raising the exception to the caller
    assert response["action"] == "escalate"
    assert "System unavailable" in response["text"]
    assert response["reason"] == "timeout"
