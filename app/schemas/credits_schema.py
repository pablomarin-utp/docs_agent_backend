from pydantic import BaseModel, Field
class UpdateCreditsRequest(BaseModel):
    """Request to update user credits."""
    credits: int = Field(..., ge=0, description="New credit amount")