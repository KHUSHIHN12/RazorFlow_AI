from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.razorpay_service import RazorpayService
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/payment", tags=["Payment"])

class CreateOrderRequest(BaseModel):
    amount_paise: int
    currency: Optional[str] = "INR"

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    amount_paise: Optional[int] = 0

@router.post("/create-order")
async def create_order_endpoint(req: CreateOrderRequest):
    try:
        order = RazorpayService.create_order(amount_paise=req.amount_paise, currency=req.currency)
        return order
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/verify")
async def verify_payment_endpoint(req: VerifyPaymentRequest):
    try:
        is_valid = RazorpayService.verify_payment_signature(
            razorpay_order_id=req.razorpay_order_id,
            razorpay_payment_id=req.razorpay_payment_id,
            razorpay_signature=req.razorpay_signature
        )
        
        if is_valid:
            # Update merchant analytics on successful payment
            analytics_service.log_successful_payment(req.amount_paise or 0)
            return {
                "status": "success",
                "verified": True,
                "payment_id": req.razorpay_payment_id,
                "order_id": req.razorpay_order_id,
                "message": "Payment signature successfully verified via Razorpay SDK!"
            }
        else:
            return {
                "status": "failed",
                "verified": False,
                "message": "Invalid Razorpay payment signature."
            }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
