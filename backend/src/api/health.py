from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    status: str = "OK"

@router.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(status="OK")