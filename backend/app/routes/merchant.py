from fastapi import APIRouter
from pydantic import BaseModel
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/merchant", tags=["Merchant"])

class LaunchCampaignRequest(BaseModel):
    campaign_id: str

@router.get("/metrics")
async def get_merchant_metrics():
    return analytics_service.get_metrics()

@router.post("/campaign/launch")
async def launch_campaign(req: LaunchCampaignRequest):
    updated = analytics_service.launch_campaign(req.campaign_id)
    return {"status": "success", "campaign": updated}
