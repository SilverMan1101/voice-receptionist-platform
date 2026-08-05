from typing import List, Dict, Any, Optional
from services.shared_kernel.domain.schemas import BusinessRuleResponse, EscalationDecision

class BusinessRulesEngine:
    def __init__(self, rules: List[BusinessRuleResponse]):
        self.rules = rules

    def evaluate_escalation(self, 
                            trigger_type: str, 
                            context: Dict[str, Any] = None) -> Optional[EscalationDecision]:
        """
        Evaluate if an escalation should happen based on the trigger type and rules.
        trigger_types: 'explicit_request', 'low_confidence', 'turn_limit_reached', 'timeout', 'knowledge_unavailable', 'business_mandate'
        Returns EscalationDecision if escalation is required, None otherwise.
        """
        # Look for a specific rule matching this condition
        for rule in self.rules:
            if rule.rule_type == "escalation" and rule.active:
                cond = rule.condition
                if cond.get("trigger_type") == trigger_type:
                    return EscalationDecision(
                        reason=cond.get("reason", f"Escalated due to {trigger_type}"),
                        department_id=rule.action.get("department_id"),
                        fallback_message=rule.action.get("fallback_message")
                    )
        
        # Default fallbacks if no specific rule is configured (since some are hard safety rules)
        if trigger_type == "low_confidence":
            return EscalationDecision(reason="Low confidence in knowledge retrieval", fallback_message="I'm having trouble finding that information. Let me connect you with someone who can help.")
        if trigger_type == "explicit_request":
            return EscalationDecision(reason="Caller explicitly requested human", fallback_message="I will connect you to a human now.")
        if trigger_type in ["timeout", "knowledge_unavailable"]:
            return EscalationDecision(reason="System failure or timeout", fallback_message="I'm experiencing technical difficulties. Let me transfer you.")
        if trigger_type == "turn_limit_reached":
            return EscalationDecision(reason="Maximum conversation length reached", fallback_message="We've been chatting for a while. Let me connect you with a representative.")
            
        return None
