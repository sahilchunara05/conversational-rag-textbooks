from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def check_health():
    """Confirms the API and service health status."""
    return {"status": "healthy"}
