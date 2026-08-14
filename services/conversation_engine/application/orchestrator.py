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
        # self.system_prompt = (
        #     "You are a helpful AI Voice Receptionist. Answer questions using ONLY the provided knowledge context. "
        #     "If you do not know the answer or the context is missing, do not guess. "
        #     "You can collect caller info if needed. You can escalate to a human if the caller asks or if you cannot help."
        # )
        self.system_prompt = (
            "You are a helpful AI Voice Receptionist for this organization. Answer questions using ONLY the "
            "provided knowledge context. If you do not know the answer or the context is missing, do not guess.\n\n"
            
            "IMPORTANT — Booking and appointments: You CANNOT check real-time appointment availability, "
            "confirm a booking, or access any live scheduling system. Never say things like 'let me check "
            "our system' or 'I'll book that for you' — you have no tool that does this. "
            "If a caller wants to book an appointment: "
            "1) Use collect_caller_info to capture their name, contact info, and requested date/time as a lead. "
            "2) Once you have enough info, tell them clearly: 'I've noted your request for [date/time] — our team "
            "will confirm availability and call you back to finalize it.' Do NOT imply the appointment is confirmed. "
            "3) Only use trigger_escalation for booking if the caller explicitly asks to speak to a human, or if "
            "they seem frustrated — not simply because they gave you a date.\n\n"
            
            "IMPORTANT — Escalation: Only call trigger_escalation when the caller explicitly asks for a human, "
            "or clearly indicates they want to stop talking to the AI. Do not escalate just because you're unsure "
            "what to do next — if you're stuck, ask a clarifying question or use collect_caller_info instead. "
            "Pay close attention to negations — if a caller says 'no' to being transferred, do not transfer them.\n\n"

            "Only call collect_caller_info once per field. If you already have a piece of information "
            "(check the conversation history), do not collect it again — move on to asking for the next "
            "missing field, or produce your reply if you have everything you need."
            "Never invent, guess, or use a placeholder value (like 'unknown' or 'caller') for collect_caller_info. "
            "Only call it with information the caller has explicitly stated in this conversation.\n\n"  
            
            "You can also end the call if the conversation has naturally concluded."
        )

    def process_turn(self, call_id: str, organization_id: str, token: str, user_text: str) -> Dict[str, Any]:

        if not user_text or not user_text.strip():
            return {"action": "reply", "text": "I didn't catch that — could you repeat?"}
    
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
        seen_tool_calls = set()  # NEW — tracks (tool_name, args) already executed this turn
        duplicate_block_count = 0 
        max_tool_iterations = 6
        
        for _ in range(max_tool_iterations):
            try:
                response = self.llm.generate_response(self.system_prompt, turns, context=context)
            # except Exception as e:
            #     # LLM timeout or failure -> degrade
            #     decision = self.rules_engine.evaluate_escalation("timeout")
            #     return self._execute_escalation(call_id, decision)
            except Exception as e:
                import traceback
                traceback.print_exc()
                decision = self.rules_engine.evaluate_escalation("timeout")
                return self._execute_escalation(call_id, decision)
                
            if response["type"] == "message":
                self.state.add_turn(call_id, "ai", response["text"])
                return {"action": "reply", "text": response["text"]}
                
            elif response["type"] == "tool_call":
                tool_name = response["name"]
                args = response["arguments"]
                print(f"[DEBUG] Tool call attempted: {tool_name} | args: {args}")  # temporary

                if tool_name == "collect_caller_info":
                    field_name = args.get("field_name")
                    field_value = args.get("field_value")
                    call_signature = (tool_name, field_name, field_value)

                    already_persisted = self.state.get_collected_info(call_id).get(field_name) is not None

                    if call_signature in seen_tool_calls or already_persisted:
                        duplicate_block_count += 1
                        
                        if duplicate_block_count >= 2:
                            # Engine takes over: model isn't listening to corrective notes.
                            # Stop looping and force a deterministic reply instead of trusting the LLM further.
                            collected = self.state.get_collected_info(call_id)
                            missing = [f for f in ["name", "phone_number", "requested_date_time"] if f not in collected]
                            if missing:
                                text = f"Thanks! Could you also share your {missing[0].replace('_', ' ')}?"
                            else:
                                text = "Thank you — I've noted all your details. Our team will confirm and call you back to finalize your appointment."
                            self.state.add_turn(call_id, "ai", text)
                            return {"action": "reply", "text": text}
                        
                        turns.append(CallTurnBase(
                            turn_index=999, speaker="system",
                            text=f"You already have {field_name}='{field_value}'. Do not call collect_caller_info for "
                                f"this field again. Ask for the next missing detail, or reply now."
                        ))
                        continue

                    seen_tool_calls.add(call_signature)
                    self.state.add_collected_info(call_id, field_name, field_value)
                    turns.append(CallTurnBase(turn_index=999, speaker="system", text=f"Collected {field_name} = {field_value}"))
                    continue
                
                # VALIDATION LAYER (Engine controls side-effects)
                elif tool_name == "retrieve_knowledge":
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
                    # except Exception as e:
                    #     # Client timeout or connection error -> degrade safely
                    #     decision = self.rules_engine.evaluate_escalation("timeout")
                    #     return self._execute_escalation(call_id, decision)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        decision = self.rules_engine.evaluate_escalation("timeout")
                        return self._execute_escalation(call_id, decision)
                        
                # elif tool_name == "collect_caller_info":
                #     self.state.add_collected_info(call_id, args.get("field_name"), args.get("field_value"))
                #     # Inform LLM it succeeded by injecting a system turn
                #     turns.append(CallTurnBase(turn_index=999, speaker="system", text=f"Collected {args.get('field_name')} = {args.get('field_value')}"))
                #     continue
                    
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
        print("[DEBUG] Exhausted max_tool_iterations without a final reply")  # temporary
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
