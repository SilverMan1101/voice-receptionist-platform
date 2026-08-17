import os
import uuid
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from libs.llm_adapters.gemini_adapter import GeminiAdapter
from services.conversation_engine.infrastructure.redis_store import CallStateStore
from services.conversation_engine.infrastructure.knowledge_client import KnowledgeClient
from services.conversation_engine.application.orchestrator import ConversationOrchestrator
from services.shared_kernel.domain.schemas import BusinessRuleResponse
from services.shared_kernel.core.database import get_db
from services.shared_kernel.domain import models, schemas
from libs.auth.jwt_validator import get_current_token_data
from dotenv import load_dotenv

from libs.llm_adapters.gemini_adapter import GeminiAdapter
from services.conversation_engine.infrastructure.redis_store import CallStateStore
from services.conversation_engine.infrastructure.knowledge_client import KnowledgeClient
from services.conversation_engine.application.orchestrator import ConversationOrchestrator
from services.shared_kernel.domain.schemas import BusinessRuleResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Conversation Engine API")

# Initialize global dependencies for the Engine
llm_adapter = GeminiAdapter(model_name="gemini-3.5-flash-lite")
state_store = CallStateStore(redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
knowledge_client = KnowledgeClient(base_url=os.environ.get("KNOWLEDGE_SERVICE_URL", "http://127.0.0.1:8001"))

# Mock rules for now since Tenant Config is partially mocked in this phase
MOCK_RULES = [
    BusinessRuleResponse(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        rule_type="escalation",
        condition={"trigger_type": "explicit_request"},
        action={"fallback_message": "Connecting you to our team now."},
        active=True
    ),
    BusinessRuleResponse(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        rule_type="escalation",
        condition={"trigger_type": "low_confidence"},
        action={"fallback_message": "I want to make sure you get the right answer. Transferring you to a specialist."},
        active=True
    )
]

orchestrator = ConversationOrchestrator(
    llm_adapter=llm_adapter,
    state_store=state_store,
    knowledge_client=knowledge_client,
    rules=MOCK_RULES
)

class TurnRequest(BaseModel):
    call_id: str
    organization_id: str
    token: str
    user_text: str

class TurnResponse(BaseModel):
    action: str
    text: Optional[str] = None
    reason: Optional[str] = None
    department_id: Optional[str] = None

@app.post("/internal/conversation/turn", response_model=TurnResponse)
async def process_turn(request: TurnRequest):
    """
    Processes a single text turn from the caller, coordinates with the LLM,
    knowledge retrieval, and rules engine, and returns the next action.
    """
    try:
        response = orchestrator.process_turn(
            call_id=request.call_id,
            organization_id=request.organization_id,
            token=request.token,
            user_text=request.user_text
        )
        return TurnResponse(**response)
    except Exception as e:
        # Fallback in case of absolute failure at the endpoint level
        return TurnResponse(
            action="escalate",
            text="I'm sorry, I'm experiencing technical difficulties. Transferring you now.",
            reason="internal_error"
        )

@app.get("/api/v1/calls", response_model=List[schemas.CallResponse])
def list_calls(
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    return db.query(models.Call).filter(
        models.Call.organization_id == token_data.organization_id
    ).order_by(models.Call.started_at.desc()).all()

@app.get("/api/v1/calls/{call_id}", response_model=schemas.CallDetailResponse)
def get_call_detail(
    call_id: str,
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    call = db.query(models.Call).filter(
        models.Call.id == call_id,
        models.Call.organization_id == token_data.organization_id
    ).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
        
    return call
