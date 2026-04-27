from fastapi import APIRouter, Response, status
from services.dashboard_service import get_dashboard

router = APIRouter()

@router.get("/get")
async def function(user_id: str, response: Response):
    try:
        return await get_dashboard(user_id)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "message": "Internal Server Error",
            "metadata": {
                "error": str(e)
            }
        }