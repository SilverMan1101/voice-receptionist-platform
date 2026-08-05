import pytest
import uuid
from services.shared_kernel.domain.schemas import BusinessRuleResponse
from services.conversation_engine.domain.business_rules_engine import BusinessRulesEngine

def test_evaluate_explicit_request():
    rules = [
        BusinessRuleResponse(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            rule_type="escalation",
            condition={"trigger_type": "explicit_request"},
            action={"fallback_message": "Transferring you to a human.", "department_id": str(uuid.uuid4())},
            active=True
        )
    ]
    engine = BusinessRulesEngine(rules)
    decision = engine.evaluate_escalation("explicit_request")
    
    assert decision is not None
    assert decision.fallback_message == "Transferring you to a human."
    assert decision.department_id is not None

def test_evaluate_low_confidence():
    rules = [
        BusinessRuleResponse(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            rule_type="escalation",
            condition={"trigger_type": "low_confidence"},
            action={"fallback_message": "Let me get someone who can help."},
            active=True
        )
    ]
    engine = BusinessRulesEngine(rules)
    decision = engine.evaluate_escalation("low_confidence")
    
    assert decision is not None
    assert decision.fallback_message == "Let me get someone who can help."

def test_evaluate_fallback_when_no_rule():
    engine = BusinessRulesEngine([]) # No rules
    decision = engine.evaluate_escalation("low_confidence")
    
    assert decision is not None
    assert decision.reason == "Low confidence in knowledge retrieval"
    
def test_evaluate_turn_limit():
    engine = BusinessRulesEngine([])
    decision = engine.evaluate_escalation("turn_limit_reached")
    assert decision is not None
    assert decision.reason == "Maximum conversation length reached"
