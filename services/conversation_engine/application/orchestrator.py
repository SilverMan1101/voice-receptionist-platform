from typing import Dict, Any, List
from services.shared_kernel.domain.schemas import CallTurnBase, BusinessRuleResponse, EscalationDecision
from libs.llm_adapters.base import BaseLLMAdapter
from services.conversation_engine.domain.business_rules_engine import BusinessRulesEngine
from services.conversation_engine.infrastructure.redis_store import CallStateStore
from services.conversation_engine.infrastructure.knowledge_client import KnowledgeClient

class ConversationOrchestrator:
    def __init__(self, 
                 llm_adapter: BaseLLMAdapter, 
                 state_store: CallStateStore,
                 knowledge_client: KnowledgeClient,
                 rules: List[BusinessRuleResponse]):
        self.llm = llm_adapter
        self.state = state_store
        self.knowledge_client = knowledge_client
        self.rules_engine = BusinessRulesEngine(rules)
        self.system_prompt = (
            "You are a helpful AI Voice Receptionist. Answer questions using ONLY the provided knowledge context. "
            "If you do not know the answer or the context is missing, do not guess. "
            "You can collect caller info if needed. You can escalate to a human if the caller asks or if you cannot help."
        )

    def process_turn(self, call_id: str, organization_id: str, token: str, user_text: str) -> Dict[str, Any]:
        # 1. Add user turn to state
        self.state.add_turn(call_id, "caller", user_text)
        
        # 2. Get history
        history_dicts = self.state.get_turns(call_id)
        turns = [CallTurnBase(turn_index=t.get("turn_index", i), speaker=t["speaker"], text=t["text"]) 
                 for i, t in enumerate(history_dicts)]
        
        # Check turn limit
        if len(turns) >= 20:
            decision = self.rules_engine.evaluate_escalation("turn_limit_reached")
            if decision:
                return self._execute_escalation(call_id, decision)

        context = ""
        # 3. Tool Calling Loop
        max_tool_iterations = 3
        
        for _ in range(max_tool_iterations):
            try:
                response = self.llm.generate_response(self.system_prompt, turns, context=context)
            except Exception as e:
                # LLM timeout or failure -> degrade
                decision = self.rules_engine.evaluate_escalation("timeout")
                return self._execute_escalation(call_id, decision)
                
            if response["type"] == "message":
                self.state.add_turn(call_id, "ai", response["text"])
                return {"action": "reply", "text": response["text"]}
                
            elif response["type"] == "tool_call":
                tool_name = response["name"]
                args = response["arguments"]
                
                # VALIDATION LAYER (Engine controls side-effects)
                if tool_name == "retrieve_knowledge":
                    try:
                        results = self.knowledge_client.query(token, args.get("query", ""))
                        if not results:
                            # Adversarial / No matches
                            decision = self.rules_engine.evaluate_escalation("knowledge_unavailable")
                            if decision:
                                return self._execute_escalation(call_id, decision)
                            
                        # Use the actual is_confident flag from knowledge_service
                        best_match = results[0]
                        if not best_match.get("is_confident", False):
                            decision = self.rules_engine.evaluate_escalation("low_confidence")
                            if decision:
                                return self._execute_escalation(call_id, decision)
                            
                        context = "\n".join([r["text"] for r in results if r.get("is_confident")])
                        # Continue loop to ask LLM again with context
                        continue
                    except Exception as e:
                        # Client timeout or connection error -> degrade safely
                        decision = self.rules_engine.evaluate_escalation("timeout")
                        return self._execute_escalation(call_id, decision)
                        
                elif tool_name == "collect_caller_info":
                    self.state.add_collected_info(call_id, args.get("field_name"), args.get("field_value"))
                    # Inform LLM it succeeded by injecting a system turn
                    turns.append(CallTurnBase(turn_index=999, speaker="system", text=f"Collected {args.get('field_name')} = {args.get('field_value')}"))
                    continue
                    
                elif tool_name == "trigger_escalation":
                    decision = self.rules_engine.evaluate_escalation("explicit_request")
                    if decision:
                        return self._execute_escalation(call_id, decision)
                    # If no specific decision, just use a generic one
                    return self._execute_escalation(call_id, EscalationDecision(reason="Requested", fallback_message="Transferring now."))
                    
                elif tool_name == "end_call":
                    return {"action": "end_call", "reason": args.get("reason", "Finished")}
                
                else:
                    # Invalid tool call (LLM trying to hallucinate a tool) -> ignore and degrade
                    decision = self.rules_engine.evaluate_escalation("timeout")
                    return self._execute_escalation(call_id, decision)
                    
        # If we loop too many times on tools
        decision = self.rules_engine.evaluate_escalation("timeout")
        return self._execute_escalation(call_id, decision)

    def _execute_escalation(self, call_id: str, decision: EscalationDecision) -> Dict[str, Any]:
        # Engine validates the decision and issues the final command
        text = decision.fallback_message or "I will transfer you now."
        self.state.add_turn(call_id, "ai", text)
        return {
            "action": "escalate",
            "department_id": str(decision.department_id) if decision.department_id else None,
            "reason": decision.reason,
            "text": text
        }
