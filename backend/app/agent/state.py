from typing import List, Dict, Any, Optional, TypedDict, Annotated
import operator

class CartItem(TypedDict):
    product_id: str
    name: str
    price: float
    price_paise: int
    quantity: int
    image_url: str

class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], operator.add]
    cart: List[CartItem]
    budget_limit: Optional[float]
    pending_action: Optional[Dict[str, Any]]
    confirmation_required: bool
    active_order: Optional[Dict[str, Any]]
    response_products: List[Dict[str, Any]]
