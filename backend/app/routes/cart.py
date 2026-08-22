from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.agent.tools import manage_cart

router = APIRouter(prefix="/api/cart", tags=["Cart"])

class CartOperationRequest(BaseModel):
    cart: List[Dict[str, Any]]
    action: str # "add", "remove", "clear", "get"
    product_id: str
    quantity: Optional[int] = 1

@router.post("")
async def cart_operation(req: CartOperationRequest):
    res = manage_cart(
        cart=req.cart,
        action=req.action,
        product_id=req.product_id,
        quantity=req.quantity
    )
    return res
