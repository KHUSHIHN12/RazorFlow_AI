from typing import Dict, Any, List, Optional
from app.agent.recommendation_pipeline import recommendation_pipeline

class RazorFlowAgent:
    """
    Intelligent Agentic Commerce Engine for RazorFlow AI.
    Delegates message processing to the single authoritative Recommendation Pipeline.
    """
    
    @staticmethod
    def process_message(user_message: str,
                        current_cart: List[Dict[str, Any]],
                        confirmed_pay: bool = False,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return recommendation_pipeline.execute(
            user_message=user_message,
            current_cart=current_cart,
            confirmed_pay=confirmed_pay,
            session_context=context
        )

agent_engine = RazorFlowAgent()
