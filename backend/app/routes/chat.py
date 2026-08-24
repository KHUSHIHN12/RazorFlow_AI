from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.agent.graph import agent_engine

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    cart: Optional[List[Dict[str, Any]]] = []
    confirmed_pay: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    cart: List[Dict[str, Any]]
    products: List[Dict[str, Any]]
    confirmation_required: bool
    active_order: Optional[Dict[str, Any]] = None
    bundle_data: Optional[Dict[str, Any]] = None
    audit_logs: Optional[List[Dict[str, Any]]] = []

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        cart = req.cart or []
        result = agent_engine.process_message(
            user_message=req.message,
            current_cart=cart,
            confirmed_pay=req.confirmed_pay
        )
        return ChatResponse(
            response=result["response"],
            cart=result["cart"],
            products=result["products"],
            confirmation_required=result["confirmation_required"],
            active_order=result.get("active_order"),
            bundle_data=result.get("bundle_data"),
            audit_logs=result.get("audit_logs", [])
        )
    except Exception as ex:
        print(f"[ChatRoute] Error: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
