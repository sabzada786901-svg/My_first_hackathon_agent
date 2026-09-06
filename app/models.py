from pydantic import BaseModel, Field
from typing import Optional


class FarmerProfile(BaseModel):
    district: Optional[str] = None
    soil_type: Optional[str] = None
    season: Optional[str] = None
    water_availability: Optional[str] = None
    land_size_acres: Optional[float] = Field(default=None, gt=0)
    crop: Optional[str] = None


class CropRecommendation(BaseModel):
    crop: str
    expected_yield_per_acre: float
    expected_profit_per_acre: float
    reason: str


class FertilizerPlan(BaseModel):
    crop: str
    acres: float
    urea_bags: float
    dap_bags: float
    total_cost_pkr: float


class ProfitEstimate(BaseModel):
    crop: str
    acres: float
    expected_revenue_pkr: float
    total_cost_pkr: float
    net_profit_pkr: float
    break_even_yield: float


# ==========================================
# KISAN DOST RESPONSE
# ==========================================

class KisanDostResponse(BaseModel):
    answer: str = Field(
        ...,
        min_length=1,
        description="Final answer given to the farmer."
    )

    safety_note: Optional[str] = Field(
        default=None,
        description="Safety warning for pesticides or agricultural risks."
    )